create table books
(
    book_id     varchar(13)          not null
        primary key,
    name        varchar(45)          not null,
    lent        tinyint(1) default 0 not null,
    borrower_id int(10)              null,
    time        timestamp            null
);

create table user
(
    username varchar(16) not null,
    user_id  int(10)     not null
        primary key,
    encoding blob        not null,
    constraint username
        unique (username)
);


