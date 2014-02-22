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

# compare thermal sensation 18-28C for women younger than 30 and older than 30.
# all aggregation is done directly with SQL.
query <- 'select case when participant.age > 30 then "over 30" else "under 30" end as "age group",
          avg(t1.value) as "Avg Thermal Sensation", avg(t2.value) as "Avg drybulb temperature", count(t1.value) as "N"
          from data t1, data t2
              inner join response on response.id = t1.respid
              inner join participant on participant.id = response.partid
          where t1.fieldid="ash" 
              and t2.fieldid="ta_m"
              and t1.respid = t2.respid 
              and t2.value > 18 and t2.value < 28 
              and participant.age <> 0
          group by case when participant.age > 30 then "over 30" else "under 30" end'
res <- dbGetQuery(con, query)
print(res)

# same analysis, aggregated within R
query <- "select participant.age as 'age', t1.value as 'ash', t2.value as 'ta_m'
          from data t1, data t2
              inner join response on response.id = t1.respid
              inner join participant on participant.id = response.partid
          where t1.fieldid='ash' and t2.fieldid='ta_m'
              and t1.respid = t2.respid"
          
res <- dbGetQuery(con, query)
res <- na.omit(res)
res <- subset(res, ta_m > 18 & ta_m < 28)
by <- list(sapply(res$age, function(d) if (d > 30) "Over 30" else "Under 30"))
aggregate(res, by, mean)
table(by)
