use c9;

drop table if exists isReported;
drop table if exists tagged;
drop table if exists starred;
drop table if exists posted;
drop table if exists followed;
drop table if exists accounts;
drop table if exists posts;
drop table if exists tags;

create table accounts (
    username varchar(30) primary key,
    hashed varchar(60),
    isAdmin boolean
);

create table posts (
    pid int auto_increment primary key,
    title varchar(60) NOT NULL,
    content varchar(1000),
    time_created datetime,
    location varchar(60),
    num_starred int unsigned,
    imagefile varchar(60),
    event_time time NOT NULL,
    event_date date NOT NULL
);


create table tags (
    tid int auto_increment primary key,
    tag_name varchar(100),
    num_followers int unsigned
);

create table tagged (
    tid int NOT NULL,
    pid int NOT NULL,
    primary key (tid, pid),
    foreign key (tid) references tags(tid) on delete cascade on update cascade,
    foreign key (pid) references posts(pid) on delete cascade on update cascade
);

create table starred (
    pid int NOT NULL,
    username varchar(30) NOT NULL,
    primary key (pid, username),
    foreign key (pid) references posts(pid) on delete restrict on update cascade,
    foreign key (username) references accounts(username) on delete restrict on update cascade
);

create table posted (
    pid int NOT NULL,
    username varchar(30) NOT NULL,
    primary key (pid,username),
    foreign key (pid) references posts(pid) on delete restrict on update cascade,
    foreign key (username) references accounts(username) on delete restrict on update cascade
);

create table followed (
    tid int NOT NULL,
    username varchar(30) NOT NULL,
    primary key (tid,username),
    foreign key (tid) references tags(tid) on delete restrict on update cascade,
    foreign key (username) references accounts(username) on delete restrict on update cascade
);

create table isReported (
    pid int NOT NULL,
    username varchar(30) NOT NULL,
    primary key (pid,username),
    foreign key (pid) references posts(pid) on delete restrict on update cascade,
    foreign key (username) references accounts(username) on delete restrict on update cascade
);
