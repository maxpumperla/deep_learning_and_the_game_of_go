'use strict';

var SGFLetters = 'abcdefghijklmnopqrstuvwxyz'.split('');

/**
 * Create a helper class to create coordinates from (1,2) (zero-based),
 * 'ah' type of input. You can create a coordinate with no arguments, in
 * which case it defaults to (0,0), or with one argument, in which case it
 * tries to parse 'ai' type of string coordinate, or with two arguments, (i,j).
 * 'J18' style coordinates depend on board size due to number running from
 * bottom, so those need to be instantiated from Board.getCoordinate.
 *
 * @param {int} [i] Column or SGF-style string.
 * @param {int} [j] Row.
 * @constructor
 */
var Coordinate = function(i, j) {
  if(i !== undefined) {
    if(j !== undefined) {
      this.i = i;
      this.j = j;
    } else { // try to parse coordinates from first parameter
      this.i = 0;
      this.j = 0;

      if(typeof i != 'string')
        return;

      // assume SGF-type coordinate
      i = i.toLowerCase();

      this.i = SGFLetters.indexOf(i.substr(0,1));
      this.j = SGFLetters.indexOf(i.substr(1));
    }
  } else { // called without both parameters
    this.i = 0;
    this.j = 0;
  }
};

/**
 * Compare with another coordinate.
 *
 * @param {Coordinate} Coordinate.
 * @returns {boolean} true if equal, false if not.
 */
Coordinate.prototype.equals = function(c) {
  return (c.i == this.i) && (c.j == this.j);
};

/**
 * Make an SGF-type 'ai' string representation of the coordinate.
 *
 * @returns {string} String representation.
 */
Coordinate.prototype.toString = function() {
  return SGFLetters[this.i] + SGFLetters[this.j];
};

/**
 * Make a copy of this coordinate.
 *
 * @returns {Coordinate} A copy of this coordinate.
 */
Coordinate.prototype.copy = function() {
  return new Coordinate(this.i, this.j);
};

module.exports = Coordinate;
