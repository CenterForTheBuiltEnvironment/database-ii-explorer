# To connect to the database we use the RSQLite package.
# This can be installed by running install.packages('RSQLite')
require('RSQLite')

# Create an instance of the SQLite driver
drv <- dbDriver("SQLite")

# Create a connection to the database
con <- dbConnect(drv, dbname = '../db/ashrae.db')

# Now you're ready to run queries
# Count the number of buildings
query <- "select count(*) from building"
res <- dbGetQuery(con, query)
print(res)

# Render boxplots based on categories. 
# Show a boxplot of acceptability by sex as a category
query <- paste("select value, participant.sex
                from data
                inner join response on response.id = respid
                inner join participant on participant.id = response.id
                where fieldid = 'ash'")
res <- dbGetQuery(con, query)
boxplot(res$value~res$sex)

# or just look at the summary statistics
summary(res)

# statistics by category
# (the aggregate function will run an aggregate on each category of the data
# you provide. In this case we get the mean for each sex)
by <- list(res$sex)
aggregate(res, by, mean)

# Here we use the city as a category.
query <- paste("select value, building.city 
                from data 
                inner join response on response.id = respid
                inner join participant on participant.id = response.partid
                inner join building on building.id = participant.bldgid
                where fieldid='ash'")
res <- dbGetQuery(con, query)
boxplot(res$value~res$city)

by <- list(res$city)
aggregate(res, by, mean)
