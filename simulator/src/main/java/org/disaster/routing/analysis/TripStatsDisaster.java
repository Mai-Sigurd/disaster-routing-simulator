package org.disaster.routing.analysis;

import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.ints.IntList;
import it.unimi.dsi.fastutil.ints.IntOpenHashSet;
import it.unimi.dsi.fastutil.ints.IntSet;
import it.unimi.dsi.fastutil.objects.*;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.math3.analysis.interpolation.LoessInterpolator;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;
import org.matsim.application.ApplicationUtils;
import org.matsim.application.CommandSpec;
import org.matsim.application.MATSimAppCommand;
import org.matsim.application.options.CsvOptions;
import org.matsim.application.options.InputOptions;
import org.matsim.application.options.OutputOptions;
import org.matsim.application.options.ShpOptions;
import org.matsim.core.utils.io.IOUtils;
import picocli.CommandLine;
import tech.tablesaw.api.*;
import tech.tablesaw.columns.strings.AbstractStringColumn;
import tech.tablesaw.io.csv.CsvReadOptions;
import tech.tablesaw.joining.DataFrameJoiner;
import tech.tablesaw.selection.Selection;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static tech.tablesaw.aggregate.AggregateFunctions.count;

@CommandLine.Command(name = "trips", description = "Calculates various trip related metrics.")
@CommandSpec(
        requires = {"trips.csv", "persons.csv"},
        produces = {"trip_stats_disaster.csv"}
)
public class TripStatsDisaster implements MATSimAppCommand {

    /**
     * Attributes which relates this person to a reference person.
     */
    public static final String ATTR_REF_ID = "ref_id";
    /**
     * Person attribute that contains the reference modes of a person. Multiple modes are delimited by "-".
     */
    public static final String ATTR_REF_MODES = "ref_modes";
    /**
     * Person attribute containing its weight for analysis purposes.
     */
    public static final String ATTR_REF_WEIGHT = "ref_weight";
    private static final Logger log = LogManager.getLogger(TripStatsDisaster.class);
    @CommandLine.Option(names = "--person-filter", description = "Define which persons should be included into trip analysis. Map like: Attribute name (key), attribute value (value). " +
            "The attribute needs to be contained by output_persons.csv. Persons who do not match all filters are filtered out.", split = ",")
    private final Map<String, String> personFilters = new HashMap<>();
    @CommandLine.Mixin
    private InputOptions input = InputOptions.ofCommand(TripStatsDisaster.class);
    @CommandLine.Mixin
    private OutputOptions output = OutputOptions.ofCommand(TripStatsDisaster.class);
    @CommandLine.Option(names = "--input-ref-data", description = "Optional path to reference data", required = false)
    private String refData;
    @CommandLine.Option(names = "--match-id", description = "Pattern to filter agents by id")
    private String matchId;
    @CommandLine.Option(names = "--dist-groups", split = ",", description = "List of distances for binning", defaultValue = "0,1000,2000,5000,10000,20000")
    private List<Long> distGroups;
    @CommandLine.Option(names = "--modes", split = ",", description = "List of considered modes, if not set all will be used")
    private List<String> modeOrder;
    @CommandLine.Option(names = "--shp-filter", description = "Define how the shp file filtering should work", defaultValue = "home")
    private LocationFilter filter;
    @CommandLine.Mixin
    private ShpOptions shp;

    public static void main(String[] args) {
        new TripStatsDisaster().execute(args);
    }

    private static String cut(long dist, List<Long> distGroups, List<String> labels) {

        int idx = Collections.binarySearch(distGroups, dist);

        if (idx >= 0)
            return labels.get(idx);

        int ins = -(idx + 1);
        return labels.get(ins - 1);
    }



    private static int durationToSeconds(String d) {
        String[] split = d.split(":");
        return (Integer.parseInt(split[0]) * 60 * 60) + (Integer.parseInt(split[1]) * 60) + Integer.parseInt(split[2]);
    }


    private static Map<String, ColumnType> getColumnTypes() {
        Map<String, ColumnType> columnTypes = new HashMap<>(Map.of("person", ColumnType.TEXT,
                "trav_time", ColumnType.STRING, "wait_time", ColumnType.STRING, "dep_time", ColumnType.STRING,
                "longest_distance_mode", ColumnType.STRING, "main_mode", ColumnType.STRING,
                "start_activity_type", ColumnType.TEXT, "end_activity_type", ColumnType.TEXT,
                "first_pt_boarding_stop", ColumnType.TEXT, "last_pt_egress_stop", ColumnType.TEXT));

        // Map.of only has 10 argument max
        columnTypes.put("traveled_distance", ColumnType.LONG);
        columnTypes.put("euclidean_distance", ColumnType.LONG);

        return columnTypes;
    }

    @Override
    public Integer call() throws Exception {

        Table persons = Table.read().csv(CsvReadOptions.builder(IOUtils.getBufferedReader(input.getPath("persons.csv")))
                .columnTypesPartial(Map.of("person", ColumnType.TEXT))
                .sample(false)
                .separator(CsvOptions.detectDelimiter(input.getPath("persons.csv"))).build());

        int total = persons.rowCount();

        if (matchId != null) {
            log.info("Using id filter {}", matchId);
            persons = persons.where(persons.textColumn("person").matchesRegex(matchId));
        }

//		filter persons according to person (attribute) filter
        if (!personFilters.isEmpty()) {
            IntSet generalFilteredRowIds = null;
            for (Map.Entry<String, String> entry : personFilters.entrySet()) {
                if (!persons.containsColumn(entry.getKey())) {
                    log.warn("Persons table does not contain column for filter attribute {}. Filter on {} will not be applied.", entry.getKey(), entry.getValue());
                    continue;
                }
                log.info("Using person filter for attribute {} and value {}", entry.getKey(), entry.getValue());

                IntSet filteredRowIds = new IntOpenHashSet();

                for (int i = 0; i < persons.rowCount(); i++) {
                    Row row = persons.row(i);
                    String value = row.getString(entry.getKey());
//					only add value once
                    if (value.equals(entry.getValue())) {
                        filteredRowIds.add(i);
                    }
                }

                if (generalFilteredRowIds == null) {
                    // If generalFilteredRowIds is empty, add all elements from filteredRowIds to generalFilteredRowIds
                    generalFilteredRowIds = filteredRowIds;
                } else {
                    // If generalFilteredRowIds is not empty, retain only the elements that are also in filteredRowIds
                    generalFilteredRowIds.retainAll(filteredRowIds);
                }
            }

            if (generalFilteredRowIds != null) {
                persons = persons.where(Selection.with(generalFilteredRowIds.intStream().toArray()));
            }
        }

        log.info("Filtered {} out of {} persons", persons.rowCount(), total);

        // Home filter by standard attribute
        if (shp.isDefined() && filter == LocationFilter.home) {
            Geometry geometry = shp.getGeometry();
            GeometryFactory f = new GeometryFactory();

            IntList idx = new IntArrayList();

            for (int i = 0; i < persons.rowCount(); i++) {
                Row row = persons.row(i);
                Point p = f.createPoint(new Coordinate(row.getDouble("home_x"), row.getDouble("home_y")));
                if (geometry.contains(p)) {
                    idx.add(i);
                }
            }

            persons = persons.where(Selection.with(idx.toIntArray()));
        }

        log.info("Filtered {} out of {} persons", persons.rowCount(), total);

        Table trips = Table.read().csv(CsvReadOptions.builder(IOUtils.getBufferedReader(input.getPath("trips.csv")))
                .columnTypesPartial(getColumnTypes())
                .sample(false)
                .separator(CsvOptions.detectDelimiter(input.getPath("trips.csv"))).build());

        // Trip filter with start AND end
        if (shp.isDefined() && filter == LocationFilter.trip_start_and_end) {
            Geometry geometry = shp.getGeometry();
            GeometryFactory f = new GeometryFactory();
            IntList idx = new IntArrayList();

            for (int i = 0; i < trips.rowCount(); i++) {
                Row row = trips.row(i);
                Point start = f.createPoint(new Coordinate(row.getDouble("start_x"), row.getDouble("start_y")));
                Point end = f.createPoint(new Coordinate(row.getDouble("end_x"), row.getDouble("end_y")));
                if (geometry.contains(start) && geometry.contains(end)) {
                    idx.add(i);
                }
            }

            trips = trips.where(Selection.with(idx.toIntArray()));
//		trip filter with start OR end
        } else if (shp.isDefined() && filter == LocationFilter.trip_start_or_end) {
            Geometry geometry = shp.getGeometry();
            GeometryFactory f = new GeometryFactory();
            IntList idx = new IntArrayList();

            for (int i = 0; i < trips.rowCount(); i++) {
                Row row = trips.row(i);
                Point start = f.createPoint(new Coordinate(row.getDouble("start_x"), row.getDouble("start_y")));
                Point end = f.createPoint(new Coordinate(row.getDouble("end_x"), row.getDouble("end_y")));
                if (geometry.contains(start) || geometry.contains(end)) {
                    idx.add(i);
                }
            }

            trips = trips.where(Selection.with(idx.toIntArray()));
        }

        TripByGroupAnalysis groups = null;
        if (refData != null) {
            groups = new TripByGroupAnalysis(refData);
            groups.groupPersons(persons);
        }

        // Use longest_distance_mode where main_mode is not present
        trips.stringColumn("main_mode")
                .set(trips.stringColumn("main_mode").isMissing(),
                        trips.stringColumn("longest_distance_mode"));


        Table joined = new DataFrameJoiner(trips, "person").inner(persons);

        log.info("Filtered {} out of {} trips", joined.rowCount(), trips.rowCount());

        List<String> labels = new ArrayList<>();
        for (int i = 0; i < distGroups.size() - 1; i++) {
            labels.add(String.format("%d - %d", distGroups.get(i), distGroups.get(i + 1)));
        }
        labels.add(distGroups.get(distGroups.size() - 1) + "+");
        distGroups.add(Long.MAX_VALUE);

        StringColumn dist_group = joined.longColumn("traveled_distance")
                .map(dist -> cut(dist, distGroups, labels), ColumnType.STRING::create).setName("dist_group");

        joined.addColumns(dist_group);

        TextColumn purpose = joined.textColumn("end_activity_type");

        // Remove suffix durations like _345
        purpose.set(Selection.withRange(0, purpose.size()), purpose.replaceAll("_[0-9]{2,}$", ""));




        tryRun(this::writeTripStats, joined);
        return 0;
    }

    private void tryRun(ThrowingConsumer<Table> f, Table df) {
        try {
            f.accept(df);
        } catch (IOException e) {
            log.error("Error while running method", e);
        }
    }



    private void writeTripStats(Table trips) throws IOException {

        // Stats per mode
        Object2IntMap<String> n = new Object2IntLinkedOpenHashMap<>();
        Object2LongMap<String> travelTime = new Object2LongOpenHashMap<>();
        Object2LongMap<String> travelDistance = new Object2LongOpenHashMap<>();
        Object2LongMap<String> beelineDistance = new Object2LongOpenHashMap<>();

        for (Row trip : trips) {
            String mainMode = trip.getString("main_mode");

            n.mergeInt(mainMode, 1, Integer::sum);
            travelTime.mergeLong(mainMode, durationToSeconds(trip.getString("trav_time")), Long::sum);
            travelDistance.mergeLong(mainMode, trip.getLong("traveled_distance"), Long::sum);
            beelineDistance.mergeLong(mainMode, trip.getLong("euclidean_distance"), Long::sum);
        }
        String m = "car";
        try (CSVPrinter printer = new CSVPrinter(Files.newBufferedWriter(output.getPath("trip_stats_disaster.csv")), CSVFormat.DEFAULT)) {

            printer.print("Info");
            printer.print(m);

            printer.println();

            printer.print("Number of cars");
            printer.print(n.getInt(m));

            printer.println();

            printer.print("Total time traveled [h]");
            long seconds = travelTime.getLong(m);
            printer.print(new BigDecimal(seconds / (60d * 60d)).setScale(0, RoundingMode.HALF_UP));

            printer.println();

            printer.print("Total distance traveled [km]");
            double meter = travelDistance.getLong(m);
            printer.print(new BigDecimal(meter / 1000d).setScale(0, RoundingMode.HALF_UP));

            printer.println();

            printer.print("Avg. speed [km/h]");
            double speed = (travelDistance.getLong(m) / 1000d) / (travelTime.getLong(m) / (60d * 60d));
            printer.print(new BigDecimal(speed).setScale(2, RoundingMode.HALF_UP));

            printer.println();

            printer.print("Avg. beeline speed [km/h]");
            double speed_bee = (beelineDistance.getLong(m) / 1000d) / (travelTime.getLong(m) / (60d * 60d));
            printer.print(new BigDecimal(speed_bee).setScale(2, RoundingMode.HALF_UP));

            printer.println();

            printer.print("Avg. distance per trip [km]");
            double avg = (travelDistance.getLong(m) / 1000d) / (n.getInt(m));
            printer.print(new BigDecimal(avg).setScale(2, RoundingMode.HALF_UP));
            printer.println();

            printer.print("Avg. traveltime per trip [minutes]");
            double average = (travelTime.getLong(m) / 60d) / (n.getInt(m));
            printer.print(new BigDecimal(average).setScale(2, RoundingMode.HALF_UP));

            printer.println();
        }
    }


    /**
     * How shape file filtering should be applied.
     */
    enum LocationFilter {
        trip_start_and_end,
        trip_start_or_end,
        home,
        none
    }

    @FunctionalInterface
    private interface ThrowingConsumer<T> {
        void accept(T t) throws IOException;
    }
}
