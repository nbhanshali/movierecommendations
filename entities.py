"""CSC111 Winter 2021 Final Project: Entities File

Overview and Description
========================

This Python module contains the dataclasses and its methods as well as a function
to read the dataset. This includes the Movie class, the MovieGraph class, and the
MovieVertex class.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2021 Fatimeh Hassan, Shilin Zhang,
Dorsa Molaverdikhani, and Nimit Bhanshali.
"""
from __future__ import annotations
from typing import Set, List
import pandas as pd

RATING_BENCHMARK = 8.0


def load_dataset(movies_file: str, user_movie: Movie) -> MovieGraph:
    """
    Return a MovieGraph based on the details regarding movies in the given datasets.

    The user_movie is a Movie object that represents the user preferences for a movie, which
    will be added as a vertex in the MovieGraph.

    Each vertex added in the MovieGraph will represent a movie and each edge added will
    represent the common traits between the user_movie and all of the other vertices.

    Preconditions:
        - movies_file is the path to a CSV file corresponding to the IMDb movies data.

    >>> user = Movie('user_vertex', 'User', {2010}, {'Comedy'}, {45}, {'English'}, 5.0)
    >>> g = load_dataset('IMDb movies.csv', user)
    >>> len(g.get_neighbours(user.movie_id))
    80018
    >>> user.title in g.get_neighbours(user.movie_id)
    False
    >>> 'Miss Jerry' in g.get_neighbours(user.movie_id)
    True
    """
    movie_graph = MovieGraph()

    attributes = {'imdb_title_id', 'original_title', 'year', 'genre', 'duration', 'language',
                  'avg_vote'}
    movies = pd.read_csv(movies_file, usecols=lambda x: x in attributes)
    movie_graph.add_vertex(user_movie)

    for index in movies.index:
        movie_id = str(movies['imdb_title_id'][index])
        title = str(movies['original_title'][index])
        release_year = {int(movies['year'][index])}
        genre = set(movies['genre'][index].split(', '))
        duration = {int(movies['duration'][index])}
        language = set(str(movies['language'][index]).split(', '))
        rating = float(movies['avg_vote'][index])
        movie = Movie(movie_id, title, release_year, genre, duration, language, rating)
        movie_graph.add_vertex(movie)
        movie_graph.add_edge(user_movie.movie_id, movie_id)

    return movie_graph


class Movie:
    """
    A data class representing a movie.

    Instance Attributes:
        - movie_id: the unique IMDb title id of the movie
        - title: the title of the movie
        - release_year: the year the movie was released
        - genre: the genre(s) of the movie
        - duration: the length of the movie (in minutes)
        - language: the language the movie was written in
        - rating: the total average weighted rating the movie received

    Representation Invariants:
        - 1890 <= self.release_year <= 2020
        - 0 < self.duration < 810
        - 0.0 <= self.rating <= 10.0

    """
    movie_id: str
    title: str
    release_year: Set[int]
    genre: Set[str]
    duration: Set[int]
    language: Set[str]
    rating: float

    def __init__(self, movie_id: str, title: str, release_year: Set[int], genre: Set[str],
                 duration: Set[int], language: Set[str], rating: float) -> None:
        """Initialize a new movie object."""
        self.movie_id = movie_id
        self.title = title
        self.release_year = release_year
        self.genre = genre
        self.duration = duration
        self.language = language
        self.rating = rating


class _MovieVertex:
    """
    A vertex in the movie graph.

    Each vertex item is an instance of a Movie class.

    The neighbours is a dictionary where the key is a _MovieVertex object and the value is
    value of that key is a set of traits that the vertex and its neighbours have in common.

    A Vertex is in the neighbours of this Vertex if it has at least one trait
    in common with this Vertex.

    The structure of the attributes for this dataclass takes inspiration from the WeightedVertex
    class in Assignment 3, created by David Liu and Isaac Waller.However, we changed the
    implementation to fit our program.The vertices here are all movies so there is no kind attribute
    and the value of the neighbours is the set of common traits rather than the similarity
    score.

    Instance Attributes:
        - item: The data stored in this vertex, representing a Movie object.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)

    """

    item: Movie
    neighbours: dict[_MovieVertex, set]

    def __init__(self, item: Movie) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = {}


class MovieGraph:
    """A graph used to represent a movie network that keeps track of the common traits
    between movies.

    There will be an edge between 2 movies if and only if there is at least 1 trait in common.

    The instance attributes and the functions implemented here take inspiration from the functions
    for WeightedGraph in Assignment 3, created by David Liu and Isaac Waller but with changes that
    are specific to our movie vertex implementation and overall program.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps movie id to _MovieVertex object.
    _vertices: dict[str, _MovieVertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Movie) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices

        """
        self._vertices[item.movie_id] = _MovieVertex(item)

    def add_edge(self, item1: str, item2: str) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            common = [any(g1 == g2 for g1 in v1.item.release_year for g2 in v2.item.release_year),
                      any(g1 == g2 for g1 in v1.item.genre for g2 in v2.item.genre),
                      any(g1 == g2 for g1 in v1.item.duration for g2 in v2.item.duration),
                      any(l1 == l2 for l1 in v1.item.language for l2 in v2.item.language)]

            name = ['release_year', 'genre', 'duration', 'language']

            set_so_far = set()
            for i in range(len(common)):
                if common[i]:
                    set_so_far.add(name[i])

            v1.neighbours[v2] = set_so_far
            v2.neighbours[v1] = set_so_far
        else:
            raise ValueError

    def get_common_trait(self, item1: str, item2: str) -> set:
        """Return a set of common traits between the given movies.

        Return an empty set if item1 and item2 are not adjacent.

        Preconditions:
            - item1 and item2 are vertices in this graph

        >>> g = MovieGraph()
        >>> user = Movie('user_vertex', 'User', {2010}, {'Thriller'}, {45}, {'English'}, 5.0)
        >>> movie1 = Movie('t1', 'Movie1', {2009}, {'Thriller'}, {90}, {'English'}, 6.0)
        >>> g.add_vertex(user)
        >>> g.add_vertex(movie1)
        >>> g.add_edge(user.movie_id, movie1.movie_id)
        >>> traits = g.get_common_trait(user.movie_id, movie1.movie_id)
        >>> traits == {'genre', 'language'}
        True
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        common = set()
        for vertex in v1.neighbours:
            if vertex == v2:
                common = v1.neighbours[vertex]

        return common

    def get_neighbours(self, item: str) -> set:
        """Return a set of the neighbours of the given item.

        Note that the titles of the neighbour movies are returned, not the _Vertex objects
        themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        >>> g = MovieGraph()
        >>> user = Movie('user_vertex', 'User', {2010}, {'Comedy'}, {45}, {'English'}, 5.0)
        >>> movie1 = Movie('t1', 'Movie1', {2009}, {'Comedy'}, {90}, {'French'}, 6.0)
        >>> g.add_vertex(user)
        >>> g.add_vertex(movie1)
        >>> g.add_edge(user.movie_id, movie1.movie_id)
        >>> g.get_neighbours(user.movie_id)
        {'Movie1'}
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item.title for neighbour in v.neighbours}
        else:
            raise ValueError

    def recommend_movies(self, user: str, preferences: List[str]) -> List[str]:
        """Return a list of recommended movies in order of highest similarity score to lowest,
        given a user vertex and a list of user preferences.

        In the case two movies have the same similarity score, the movies will be ranked in terms
        of the IMDb rating they received.

        >>> g = MovieGraph()
        >>> user_vertex = Movie('user_vertex', 'User', {2009}, {'Comedy'}, {95}, {'English'}, 8.1)
        >>> movie1 = Movie('t1', 'Movie1', {2010}, {'Comedy'}, {45}, {'French'}, 8.9)
        >>> user_pref = ['genre', 'release_year', 'language', 'duration']
        >>> g.add_vertex(user_vertex)
        >>> g.add_vertex(movie1)
        >>> g.add_edge(user_vertex.movie_id, movie1.movie_id)
        >>> g.recommend_movies(user_vertex.movie_id, user_pref)
        ['Movie1']
        """
        movies = {}
        final_movies = []

        for neighbour in self._vertices[user].neighbours:
            if neighbour.item.rating >= RATING_BENCHMARK:
                movie_id = neighbour.item.movie_id
                title = neighbour.item.title
                score = self.similarity_score(user, movie_id, preferences)
                if score >= 10:
                    movies[title] = score + (neighbour.item.rating / 10)

        sorted_movies = sorted(movies.items(), key=lambda x: x[1], reverse=True)

        for movie in sorted_movies:
            final_movies.append(movie[0])

        return final_movies[:10]

    def similarity_score(self, movie: str, user: str, preferences: List[str]) \
            -> int:
        """Calculate the similarity score between a movie vertex and a user vertex, given
        the order of the user's preferences.

        Preconditions:
            - len(preferences) == 4
            - all({preferences[x] in {'genre', 'release_year', 'language', 'duration'}
            for x in range(0, 4)})

        >>> g = MovieGraph()
        >>> user_vertex = Movie('user_vertex', 'User', {2010}, {'Comedy'}, {45}, {'English'}, 8.1)
        >>> movie1 = Movie('t1', 'Movie1', {2010}, {'Comedy'}, {45}, {'French'}, 8.9)
        >>> user_pref = ['genre', 'release_year', 'language', 'duration']
        >>> g.add_vertex(user_vertex)
        >>> g.add_vertex(movie1)
        >>> g.add_edge(user_vertex.movie_id, movie1.movie_id)
        >>> g.similarity_score(user_vertex.movie_id, movie1.movie_id, user_pref)
        16
        """
        final_score = 0
        common_traits = self.get_common_trait(movie, user)

        totals = {0: 10, 1: 5, 2: 3, 3: 1}

        for i in range(0, 4):
            if preferences[i] == 'genre' and 'genre' in common_traits:
                final_score += totals[i]
            elif preferences[i] == 'release_year' and 'release_year' in common_traits:
                final_score += totals[i]
            elif preferences[i] == 'language' and 'language' in common_traits:
                final_score += totals[i]
            elif preferences[i] == 'duration' and 'duration' in common_traits:
                final_score += totals[i]

        return final_score


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # import python_ta.contracts
    # python_ta.contracts.DEBUG_CONTRACTS = False
    # python_ta.contracts.check_all_contracts()
    #
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'max-line-length': 100,
    #     'extra-imports': ['dataclasses', 'typing', 'pandas'],
    #     'allowed-io': []
    # })
