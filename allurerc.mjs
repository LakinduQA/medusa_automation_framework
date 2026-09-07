export default {
  name: "Medusa Automation Report",
  output: "allure-report",
  plugins: {
    awesome: {
      options: {
        reportName: "Medusa Automation Report",
        singleFile: true,
        reportLanguage: "en",
        groupBy: ["parentSuite", "suite", "subSuite"],
      },
    },
  },
};
