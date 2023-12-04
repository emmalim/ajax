-- Emma Lim and Jenni Yu

use el110_db;

DROP TABLE IF EXISTS `movie_viewer_rating`;

CREATE TABLE `movie_viewer_rating` (
    `urid` VARCHAR(14) NOT NULL PRIMARY KEY,
    `tt` INT NOT NULL,
    `uid` INT NOT NULL,
    `score` INT NOT NULL
)
ENGINE = InnoDB;

ALTER TABLE movie ADD COLUMN IF NOT EXISTS rating FLOAT;

-- urid combines the tt with the uid to make an id for the user's
        -- rating of the movie. it's the primary key because a
        -- user will only have 1 rating for a movie and that will
        -- be updated if the user reviews a movie multiple times
-- tt is the movie tt
-- uid is the user's uid
-- score is the score given to the movie by the user
