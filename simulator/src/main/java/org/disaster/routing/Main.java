package org.disaster.routing;

import org.matsim.api.core.v01.Scenario;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.controler.Controler;
import org.matsim.core.controler.Controller;
import org.matsim.core.controler.OutputDirectoryHierarchy;
import org.matsim.core.network.algorithms.NetworkCleaner;
import org.matsim.core.scenario.ScenarioUtils;
import org.matsim.simwrapper.SimWrapperModule;

import java.io.File;

public class Main {
    public static void main(String[] args) {
        File configFile = new File("../data/matsim/config.xml");
        String absolutePath = configFile.getAbsolutePath();
        if (!configFile.exists()) {
            System.err.printf("Config file not found: %s\n", absolutePath);
            System.exit(1);
        }

        Config config = ConfigUtils.loadConfig(absolutePath);

        File outputDir = new File(configFile.getParent(), config.controller().getOutputDirectory());
        config.controller().setOutputDirectory(outputDir.getAbsolutePath());

        config.network().setTimeVariantNetwork(true);
        config.controller().setOverwriteFileSetting(
            OutputDirectoryHierarchy.OverwriteFileSetting.deleteDirectoryIfExists
        );

        Scenario scenario = ScenarioUtils.loadScenario(config);
        new NetworkCleaner().run(scenario.getNetwork());

        Controller controller = new Controler(scenario);
        controller.addOverridingModule(new SimWrapperModule());
        controller.run();
    }
}
