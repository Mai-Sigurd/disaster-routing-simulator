package org.disaster.routing;

import org.apache.logging.log4j.LogManager;
import org.matsim.api.core.v01.Scenario;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.config.groups.RoutingConfigGroup;
import org.matsim.core.controler.Controler;
import org.matsim.core.controler.Controller;
import org.matsim.core.controler.OutputDirectoryHierarchy;
import org.matsim.core.scenario.ScenarioUtils;
import org.matsim.simwrapper.SimWrapperModule;

import java.io.File;

public class Main {
    private static final String MATSIM_DIRECTORY = "../data/matsim";
    private static final String DEFAULT_OUTPUT_DIRECTORY_NAME = "output";

    public static void main(String[] args) {
        if (args.length > 1) {
            System.err.println("Usage: Main <output-directory-name>");
            System.exit(1);
        }

        File outputDirectory = new File(MATSIM_DIRECTORY, args.length == 1 ? args[0] : DEFAULT_OUTPUT_DIRECTORY_NAME);
        File configFile = new File(MATSIM_DIRECTORY, "config.xml");
        if (!configFile.exists()) {
            System.err.printf("Config file not found: %s\n", configFile.getAbsolutePath());
            System.exit(1);
        }

        Config config = ConfigUtils.loadConfig(configFile.getAbsolutePath());
        config.routing().setNetworkRouteConsistencyCheck(RoutingConfigGroup.NetworkRouteConsistencyCheck.disable);
        config.network().setTimeVariantNetwork(true);

        config.controller().setOutputDirectory(outputDirectory.getAbsolutePath());
        config.controller().setOverwriteFileSetting(
            OutputDirectoryHierarchy.OverwriteFileSetting.deleteDirectoryIfExists
        );

        Scenario scenario = ScenarioUtils.loadScenario(config);

        Controller controller = new Controler(scenario);
        controller.addOverridingModule(new SimWrapperModule());
        controller.addOverridingModule(new DisasterRoutingModule());
        controller.run();

        // Explicitly shutdown log4j2 to prevent lingering threads
        LogManager.shutdown();
    }
}
