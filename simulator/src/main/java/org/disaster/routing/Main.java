package org.disaster.routing;

import org.matsim.api.core.v01.Scenario;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.controler.Controler;
import org.matsim.core.controler.Controller;
import org.matsim.core.controler.OutputDirectoryHierarchy;
import org.matsim.core.scenario.ScenarioUtils;

import java.io.File;

public class Main {
    public static void main(String[] args) {
        File configFile = new File("../data/matsim/config.xml");
        String absolutePath = configFile.getAbsolutePath();
        if (!configFile.exists()) {
            System.err.println("Config file not found at: " + absolutePath);
            System.exit(1);
        }

        Config config = ConfigUtils.loadConfig(absolutePath);
        File outputDir = new File(configFile.getParent(), config.controller().getOutputDirectory());

        config.controller().setOutputDirectory(outputDir.getAbsolutePath());
        config.network().setTimeVariantNetwork(true);
        config.controller().setOverwriteFileSetting(
            OutputDirectoryHierarchy.OverwriteFileSetting.overwriteExistingFiles
        );

        Scenario scenario = ScenarioUtils.loadScenario(config);

        Controller controller = new Controler(scenario);
        controller.run();
    }
}
