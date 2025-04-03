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
@CommandLine.Command(name = "people-in-safety", description = "Amount of people in safety")
@CommandSpec(requires = "trips.csv", produces = "people_in_safety.csv")
public class PeopleInSafetyXY implements MATSimAppCommand {
    @CommandLine.Mixin
    private final InputOptions input = InputOptions.ofCommand(PeopleInSafetyXY.class);
    @CommandLine.Mixin
    private final OutputOptions output = OutputOptions.ofCommand(PeopleInSafetyXY.class);

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

        IntColumn traveltimeBins = IntColumn.create("traveltime_1min");

        for (Row trip : trips) {
            LocalTime dep = trip.getTime("dep_time");
            LocalTime trav = trip.getTime("trav_time");
            LocalTime arr = dep.plusSeconds(trav.toSecondOfDay());

            traveltimeBins.append(roundUpTo1(arr));
        }

        trips.addColumns(traveltimeBins);

        Table tTraveltime = trips.summarize("trip_id", count).by("end_activity_type", "traveltime_1min");
        tTraveltime.column(0).setName("purpose");
        tTraveltime.column(1).setName("bin");
        tTraveltime.replaceColumn(2, tTraveltime.numberColumn(2).divide(tTraveltime.numberColumn(2).sum()).setName("traveltime"));

        tTraveltime.doubleColumn("traveltime").setMissingTo(0.0);

        StringColumn time = StringColumn.create("time", tTraveltime.rowCount());
        for (int i = 0; i < tTraveltime.rowCount(); i++) {
            time.set(i, LocalTime.ofSecondOfDay(tTraveltime.intColumn("bin").getInt(i) * 60L).toString());
        }
        tTraveltime.addColumns(time);

        tTraveltime.sortOn("purpose", "bin");

        tTraveltime.write().csv(output.getPath("people_in_safety.csv").toFile());
        return 0;
    }

    /**
     * Rounds up the time to the nearest 10-minute interval.
     *
     * @param time The time to be rounded up.
     * @return The rounded time bin as an integer.
     */
    private static int roundUpTo1(LocalTime time) {
        int minutes = Math.max(time.getHour() * 60 + time.getMinute(), 1);
        return (int) Math.ceil(minutes);
    }
}
