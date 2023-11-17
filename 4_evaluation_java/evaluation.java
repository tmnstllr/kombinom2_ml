package me.timon;

import org.jpmml.evaluator.*;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        String modelPath = System.getProperty("user.dir") + "/model_new.pmml";
        String csvPath = System.getProperty("user.dir") + "/pred_no_preprocess.csv";
        System.out.println("Loading Model from " + modelPath);
        System.out.println("Loading Predictions from " + csvPath);

        // create model evaluator from stored model
        File pmmlFile = new File(modelPath);
        ModelEvaluator<?> modelEvaluator = new LoadingModelEvaluatorBuilder()
                .load(pmmlFile)
                .build();

        modelEvaluator.verify();

        System.out.println("Model verified.");

        List<InputField> inputFields =  modelEvaluator.getInputFields();
        System.out.println("Input fields: " + inputFields);

        List<TargetField> targetFields = modelEvaluator.getTargetFields();
        System.out.println("Target field(s): " + targetFields);

        List<OutputField> outputFields = modelEvaluator.getOutputFields();
        System.out.println("Output fields: " + outputFields);

        // read csv file
        BufferedReader reader = new BufferedReader(new FileReader(csvPath));
        reader.readLine(); // skip header

        String line;
        double sumSquaredTotal = 0.0;
        double sumSquaredResiduals = 0.0;
        double meanActual; // calculate mean of count_corrected
        int n = 0;
        double sumCountCorrected = 0.0;

        int lines = 0;

        // calculate sum of count_corrected from csv
        while ((line = reader.readLine()) != null) {
            String[] row = line.split(",");
            float actual = Float.parseFloat(row[12]);
            sumCountCorrected += actual;
            lines++;
        }

        meanActual = sumCountCorrected / lines;

        System.out.println("Count Corrected Sum : " + sumCountCorrected);
        System.out.println("Mean Actual         : " + meanActual);

        // reset reader so we can start again
        reader = new BufferedReader(new FileReader(csvPath));
        reader.readLine(); // skip csv header

        int evaluationSuccess = 0;

while ((line = reader.readLine()) != null) {
    n++;
    String[] row = line.split(",");
    // map csv columns to model features
    Map<String, ?> arguments = Map.ofEntries(
            Map.entry("month", row[0]),
            Map.entry("startClusterID", row[1]),
            Map.entry("endClusterID", row[2]),
            Map.entry("isSchoolHoliday", row[3]),
            Map.entry("isWeekend", row[4]),
            Map.entry("weekday_number", row[5]),
            Map.entry("x7", row[6]),
            Map.entry("x8", row[7]),
            Map.entry("x9", row[8]),
            Map.entry("x10", row[9]),
            Map.entry("x11", row[10]),
            Map.entry("x12", row[11]),
            Map.entry("x13", row[13]),
            Map.entry("x14", row[14]),
            Map.entry("x15", row[15]),
            Map.entry("x16", row[16]),
            Map.entry("x17", row[17]),
            Map.entry("x18", row[18]),
            Map.entry("x19", row[19])
    );

    // evaluate and calculate statistics
    try {
        Map<String, ?> results = modelEvaluator.evaluate(
                arguments);
        results = EvaluatorUtil.decodeAll(results);
        float actual = Float.parseFloat(row[12]);
        float predicted = Float.parseFloat(
                results.get("count_corrected").toString());
        float error = actual - predicted;
        sumSquaredResiduals += Math.pow(error, 2);
        sumSquaredTotal += Math.pow(actual - meanActual, 2);
        evaluationSuccess++;
            } catch (Exception e) {
                System.err.print("Unable to evaluate row " + n);
                System.err.print(Arrays.toString(row));
                System.err.println(" : " + e.getMessage());
            }
        }

        System.out.println("Sum of Squared Residuals   : " + sumSquaredResiduals);
        System.out.println("N                          : " + n);
        System.out.println("MSE                        : " + sumSquaredResiduals / n);
        System.out.println("RMSE                       : " + Math.sqrt(sumSquaredResiduals / n));
        System.out.println("R2                         : " + (1.0 - (sumSquaredResiduals / sumSquaredTotal)));
        System.out.println("Average count_corrected    : " + sumCountCorrected / n);
        System.out.println("Success Rate               : " + evaluationSuccess + "/" + n);
    }
}