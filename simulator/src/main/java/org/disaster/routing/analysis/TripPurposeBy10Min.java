package org.disaster.routing.analysis;

import org.matsim.application.CommandSpec;
import org.matsim.application.MATSimAppCommand;
import org.matsim.application.options.CsvOptions;
import org.matsim.application.options.InputOptions;
import org.matsim.application.options.OutputOptions;
import org.matsim.core.utils.io.IOUtils;
import picocli.CommandLine;
import tech.tablesaw.api.*;
import tech.tablesaw.io.csv.CsvReadOptions;
import tech.tablesaw.joining.DataFrameJoiner;

import java.io.IOException;
import java.time.LocalTime;
import java.util.Map;

import static tech.tablesaw.aggregate.AggregateFunctions.count;

/**
 * This class processes trip data to calculate trip purposes
 * aggregated into 10-minute intervals. It reads a CSV file containing trip
 * information, processes the departure and arrival times, and outputs
 * a summarized CSV file with hourly trip purpose distributions.
 */
@CommandLine.Command(name = "trip-purpose-10min", description = "Trip purposes by 10-minute intervals")
@CommandSpec(requires = "trips.csv", produces = "trip_purposes_by_10_minutes.csv")
public class TripPurposeBy10Min implements MATSimAppCommand {
    @CommandLine.Mixin
    private final InputOptions input = InputOptions.ofCommand(TripPurposeBy10Min.class);
    @CommandLine.Mixin
    private final OutputOptions output = OutputOptions.ofCommand(TripPurposeBy10Min.class);

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

        IntColumn departureBins = IntColumn.create("departure_10min");
        IntColumn arrivalBins = IntColumn.create("arrival_10min");
        IntColumn traveltimeBins = IntColumn.create("traveltime_10min");

        for (Row trip : trips) {
            LocalTime dep = trip.getTime("dep_time");
            LocalTime trav = trip.getTime("trav_time");
            LocalTime arr = dep.plusSeconds(trav.toSecondOfDay());

            departureBins.append(roundUpTo10(dep));
            arrivalBins.append(roundUpTo10(arr));
            traveltimeBins.append(roundUpTo10(trav));
        }

        trips.addColumns(departureBins, arrivalBins, traveltimeBins);

        Table tArrival = trips.summarize("trip_id", count).by("end_activity_type", "arrival_10min");
        tArrival.column(0).setName("purpose");
        tArrival.column(1).setName("bin");
        tArrival.replaceColumn(2, tArrival.numberColumn(2).divide(tArrival.numberColumn(2).sum()).setName("arrival"));

        Table tDeparture = trips.summarize("trip_id", count).by("end_activity_type", "departure_10min");
        tDeparture.column(0).setName("purpose");
        tDeparture.column(1).setName("bin");
        tDeparture.replaceColumn(2, tDeparture.numberColumn(2).divide(tDeparture.numberColumn(2).sum()).setName("departure"));

        Table tTraveltime = trips.summarize("trip_id", count).by("end_activity_type", "traveltime_10min");
        tDeparture.column(0).setName("purpose");
        tDeparture.column(1).setName("bin");
        tDeparture.replaceColumn(2, tDeparture.numberColumn(2).divide(tDeparture.numberColumn(2).sum()).setName("traveltime"));

        Table table = new DataFrameJoiner(tArrival, "purpose", "bin").fullOuter(tDeparture).sortOn("purpose", "bin");

        table.doubleColumn("departure").setMissingTo(0.0);
        table.doubleColumn("arrival").setMissingTo(0.0);
        table.doubleColumn("traveltime").setMissingTo(0.0);

        StringColumn time = StringColumn.create("time", table.rowCount());
        for (int i = 0; i < table.rowCount(); i++) {
            time.set(i, LocalTime.ofSecondOfDay(table.intColumn("bin").getInt(i) * 60L).toString());
        }
        table.addColumns(time);

        table.write().csv(output.getPath("trip_purposes_by_10_minutes.csv").toFile());
        return 0;
    }

    /**
     * Rounds up the time to the nearest 10-minute interval.
     *
     * @param time The time to be rounded up.
     * @return The rounded time bin as an integer.
     */
    private static int roundUpTo10(LocalTime time) {
        int minutes = Math.max(time.getHour() * 60 + time.getMinute(), 1);
        return (int) Math.ceil(minutes / 10.0) * 10;
    }
}
