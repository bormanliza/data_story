# Datasets and Preprocessing

At first, each member of the team had to find datasets to match the perspectives for our research. During the first team call, every dataset was discussed along with possible correlations. In the end, we chose the Urban quality and Happiness index and the overall ua scores datasets from Kaggle as a starting point, as these datasets have correlations that could be of use for a potential topic. After some brainstorming during team meetings, we came to the conclusion to focus on the welbeing of citizens in Europian capitals, as the datasets contain sufficient variables that can be used for two perspectives: 'influences of economic prosperity' and 'influences of environmental prosperity'.

During our project, we encountered new insights and, after consulting with our TA, decided to look for additional datasets. For our project, we primarily focused on the correlation of various variables with the happiness score, as it provided an indication of the well-being of people within a particular city.

#### Cleaning

We had to go through two phases in order to clean everything properly. At first we renamed columns and restructured them to merge them together. We manually merged the columns by inspecting them and merging the ones that contained extra data on overlapping cities.

It resluted several sets. One has a total of 34 columns spanning 2 datasets that first were two datasets with 19 and 16 columns. (One column (city) remains the same)

#### Variable descriptions

The variables in the final datasets can be classified in the following order:

- Continuous / Ratio variables: `Happiness_Score`, `Healthcare`, `Education`, `Economy`, `Profit`, `lat`, `lng`, `Air_Quality_Index`, `Pollution`

- Discrete / Nominal variables: `City`, `Country`
