.header on
.mode column

-- Some example aggreagation queries:

-- Average air velocity for sensation between -0.7 and 1.5
SELECT AVG(t1.value) as 'Average velocity (mid)'
FROM data t1, data t2
WHERE t1.respid = t2.respid and
      t1.fieldid = 'vel_m' and
      t2.fieldid = 'ash' and
      t2.value > -0.7 and
      t2.value < 1.5;

-- Average velocity by sensation category
SELECT AVG(t1.value) as 'Average velocity (mid)', 
       ROUND(t2.value) as 'ASH'
FROM data t1, data t2
WHERE t1.respid = t2.respid and
      t1.fieldid = 'vel_m' and
      t2.fieldid = 'ash'
GROUP BY ROUND(t2.value);

-- Show available fields 
SELECT *
FROM field;

-- Count number of buildings in database
SELECT COUNT(id) as '# Buildings'
FROM building;

-- Average sensation for high and low air velocity 
SELECT CASE WHEN t1.value > 0.2 THEN 'High' ELSE 'Low' END as 'vel-cat',
       AVG(t2.value) as 'Average thermal sensation'
FROM data t1, data t2
WHERE t1.fieldid = 'vel_m' and
      t2.fieldid = 'ash' and
      t1.respid = t2.respid
GROUP BY CASE WHEN t1.value > 0.2 THEN 'High' ELSE 'Low' END;

-- Average sensation by age group
SELECT CAST((p.age / 10) as INTEGER) * 10 as 'Age group',
       AVG(d.value) as 'Average sensation'
FROM participant p
INNER JOIN response r on p.id = r.partid
INNER JOIN data d on r.id = d.respid
WHERE d.fieldid = 'ash'
GROUP BY CAST((p.age / 10) as INTEGER) * 10;

-- Average sensation by sex
SELECT p.sex as 'Sex',
       AVG(d.value) as 'Average sensation'
FROM participant p
INNER JOIN response r on p.id = r.partid
INNER JOIN data d on r.id = d.respid
WHERE d.fieldid = 'ash'
GROUP BY p.sex;

-- Air movement preference for sensation categories
SELECT CASE WHEN t1.value > 0.2 THEN 'High' ELSE 'Low' END as 'vel-cat',
       100 * SUM(CASE WHEN t2.value = 1 THEN 1 ELSE 0 END) / COUNT(t2.value) as '% want less',
       100 * SUM(CASE WHEN t2.value = 2 THEN 1 ELSE 0 END) / COUNT(t2.value) as '% no change',
       100 * SUM(CASE WHEN t2.value = 3 THEN 1 ELSE 0 END) / COUNT(t2.value) as '% want more'
FROM data t1, data t2, data t3
WHERE t1.fieldid = 'vel_m' and
      t2.fieldid = 'avm' and
      t3.fieldid = 'ash' and 
      t1.respid = t2.respid and
      t1.respid = t3.respid and
      t3.value < 1.5 and
      t3.value > -0.7
GROUP BY CASE WHEN t1.value > 0.2 THEN 'High' ELSE 'Low' END;
