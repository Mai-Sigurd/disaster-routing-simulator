package org.disaster.routing;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.FileWriter;
import java.io.IOException;
import java.io.StringWriter;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class CSVWriter {
    public static void main(String[] args) throws IOException {
        List<XYTimeValue> values = java.util.stream.IntStream.range(0, 250)
                .mapToObj(i -> new XYTimeValue(i, i, i, i)).toList();
        writeToCSV("output.csv", values);
    }

    public static void writeToCSV(String filename, List<XYTimeValue> values) throws IOException {
        StringWriter sw = new StringWriter();
        CSVFormat csvFormat = CSVFormat.DEFAULT.builder().setHeader(XYTimeValue.HEADERS).get();

        try (final CSVPrinter printer = new CSVPrinter(sw, csvFormat)) {
            values.forEach(
                value -> {
                    try {
                        printer.printRecord(value.time, value.x, value.y, value.value);
                    } catch (IOException e) {
                        Logger.getLogger(CSVWriter.class.getName()).log(Level.SEVERE, "An error occurred", e);
                    }
                }
            );
        }

        try (final FileWriter fileWriter = new FileWriter(filename)) {
            fileWriter.write(sw.toString());
            System.out.printf("Successfully written to %s\n", filename);
        } catch (IOException e) {
            Logger.getLogger(CSVWriter.class.getName()).log(Level.SEVERE, "An error occurred", e);
        }
    }

    public record XYTimeValue(double time, double x, double y, double value) {
        public static final String[] HEADERS = {"time", "x", "y", "value"};
    }
}
