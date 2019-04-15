use c9;

load data local infile 'accounts-data.csv' into table accounts
    fields terminated by ','
    lines terminated by '\n'
    (username,isAdmin);
    
load data local infile 'posts-data.csv' into table posts
    fields terminated by ','
    lines terminated by '\n'
    (title,content,date_created,location,num_starred,imagefile,event_time);
    
load data local infile 'tags-data.csv' into table tags
    fields terminated by ','
    lines terminated by '\n'
    (tag_name,num_followers);
 
/*   
load data local infile 'tagged-data.csv' into table tagged
    fields terminated by ','
    lines terminated by '\n';
    
load data local infile 'posted-data.csv' into table posted
    fields terminated by ','
    lines terminated by '\n';
    
load data local infile 'starred-data.csv' into table starred
    fields terminated by ','
    lines terminated by '\n';
    
load data local infile 'followed-data.csv' into table followed
    fields terminated by ','
    lines terminated by '\n';
    
load data local infile 'isReported-data.csv' into table isReported
    fields terminated by ','
    lines terminated by '\n';
*/