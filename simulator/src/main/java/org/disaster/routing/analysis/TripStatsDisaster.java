package org.disaster.routing.analysis;


import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import org.matsim.application.CommandSpec;
import org.matsim.application.MATSimAppCommand;
import org.matsim.application.options.CsvOptions;
import org.matsim.application.options.InputOptions;
import org.matsim.application.options.OutputOptions;
import org.matsim.core.utils.io.IOUtils;
import picocli.CommandLine;
import tech.tablesaw.api.*;
import tech.tablesaw.io.csv.CsvReadOptions;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;

import it.unimi.dsi.fastutil.objects.Object2IntLinkedOpenHashMap;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import it.unimi.dsi.fastutil.objects.Object2LongMap;
import it.unimi.dsi.fastutil.objects.Object2LongOpenHashMap;
import tech.tablesaw.api.ColumnType;
import tech.tablesaw.api.Table;
import java.util.Map;

@CommandLine.Command(name = "trip-stats-disaster", description = "Trip stats disaster")
@CommandSpec(requires = "trips.csv", produces = "trip_stats_disaster.csv")
public class TripStatsDisaster   implements MATSimAppCommand {
    @CommandLine.Mixin
    private final InputOptions input = InputOptions.ofCommand(TripStatsDisaster.class);
    @CommandLine.Mixin
    private final OutputOptions output = OutputOptions.ofCommand(TripStatsDisaster.class);

    private static int durationToSeconds(String d) {
        String[] split = d.split(":");
        return (Integer.parseInt(split[0]) * 60 * 60) + (Integer.parseInt(split[1]) * 60) + Integer.parseInt(split[2]);
    }
    /**
     * Executes the data processing to group trips by their purposes
     * into 10-minute time bins, calculates the distribution of departures
     * and arrivals, and writes the results to a CSV file.
     *
     * @return 0 if the operation is successful, 1 if an error occurs.
     * @throws IOException if there is an error reading or writing files.
     */
    @Override
    public Integer call() throws IOException {
        Table trips = Table.read().csv(
                CsvReadOptions.builder(IOUtils.getBufferedReader(input.getPath("trips.csv")))
                        .columnTypesPartial(Map.of("trip", ColumnType.TEXT))
                        .sample(false)
                        .separator(CsvOptions.detectDelimiter(input.getPath("trips.csv")))
                        .build()
        );

        //// WRITE STATS METHOD

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

            printer.print("Number of trips");
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

            return 0;
        }
    }
}
