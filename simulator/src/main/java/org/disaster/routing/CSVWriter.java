package org.disaster.routing;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.FileWriter;
import java.io.IOException;
import java.io.StringWriter;
import java.util.logging.Level;
import java.util.logging.Logger;

public class CSVWriter {
    public static void main(String[] args) throws IOException {
        StringWriter sw = new StringWriter();
        CSVFormat csvFormat = CSVFormat.DEFAULT.builder().setHeader("time", "x", "y", "value").get();

        try (final CSVPrinter printer = new CSVPrinter(sw, csvFormat)) {
            for (int i = 0; i < 250; i++) {
                printer.printRecord(i, i, i, i);
            }
        }

        String outputFileName = "output.csv";
        try (final FileWriter fileWriter = new FileWriter(outputFileName)) {
            fileWriter.write(sw.toString());
            System.out.printf("Successfully written to %s\n", outputFileName);
        } catch (IOException e) {
            Logger.getLogger(CSVWriter.class.getName()).log(Level.SEVERE, "An error occurred", e);
        }
    }
}
