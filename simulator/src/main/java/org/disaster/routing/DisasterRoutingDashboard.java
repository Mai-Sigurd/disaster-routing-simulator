package org.disaster.routing;

import org.matsim.application.analysis.population.TripAnalysis;
import org.matsim.simwrapper.Dashboard;
import org.matsim.simwrapper.Header;
import org.matsim.simwrapper.Layout;
import org.matsim.simwrapper.viz.ColorScheme;
import org.matsim.simwrapper.viz.Plotly;
import tech.tablesaw.plotly.components.Axis;
import tech.tablesaw.plotly.traces.BarTrace;

public class DisasterRoutingDashboard implements Dashboard {
    @Override
    public void configure(Header header, Layout layout) {
        header.title = "Disaster Evacuation Routing Dashboard";

        createTripDataRow(layout, "departures", header.tab, "Departures", "departure");
        createTripDataRow(layout, "arrivals", header.tab, "Arrivals", "arrival");
    }

    private static void createTripDataRow(Layout layout, String dataType, String tab, String chartTitle, String metric) {
        layout.row(dataType, tab).el(Plotly.class, (viz, data) -> {
            viz.title = chartTitle;
            viz.description = "by hour and purpose";
            viz.layout = tech.tablesaw.plotly.components.Layout.builder()
                    .xAxis(Axis.builder().title("Hour").build())
                    .yAxis(Axis.builder().title("Share").build())
                    .barMode(tech.tablesaw.plotly.components.Layout.BarMode.STACK)
                    .build();

            viz.addTrace(BarTrace.builder(Plotly.OBJ_INPUT, Plotly.INPUT).build(),
                    viz.addDataset(data.compute(TripAnalysis.class, "trip_purposes_by_hour.csv")).mapping()
                            .name("purpose", ColorScheme.Spectral)
                            .x("h")
                            .y(metric)
            );
        });
    }
}
