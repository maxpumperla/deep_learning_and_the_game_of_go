'use strict';

var Coordinate = require('./coordinate');
var C = require('./constants');
var util = require('./util');

/**
 * Go board class for storing intersection states. Also has listeners that
 * are notified on any changes to the board via setType() and setMark().
 *
 * @param {int} width The width of the board
 * @param {int} [height] The height of the board
 * @constructor
 */
var Board = function(width, height) {
  this.width = width;

  if(height !== undefined)
    this.height = height;
  else { //noinspection JSSuspiciousNameCombination
    this.height = this.width;
  }

  this.listeners = [];

  this.stones = [];
  this.marks = [];

  // Initialize stones and marks
  for(var i=0; i<this.width; ++i) {
    var stoneArr = [], markArr = [];

    for(var j=0; j<this.height; ++j) {
      stoneArr.push(C.CLEAR);
      markArr.push(C.MARK.NONE);
    }

    this.stones.push(stoneArr);
    this.marks.push(markArr);
  }
};

/**
 * Add listener to the board. Listeners are passed an event object with
 * event type ('type' or 'mark'), coordinate and board members, and new
 * and old values as newVal and oldVal. Event object should be
 * considered read only.
 *
 * @param {function} func A listener callback.
 */
Board.prototype.addListener = function(func) {
  this.listeners.push(func);
};

/**
 * Remove listener from the board.
 *
 * @param {function} func A listener callback.
 */
Board.prototype.removeListener = function(func) {
  var index = this.listeners.indexOf(func);
  if(index != -1) this.listeners.splice(index, 1);
};

/**
 * Create coordinate from "J18" type of notation that depend from board size.
 *
 * @param {string} s The coordinate string.
 */
Board.prototype.getCoordinate = function(s) {
  return new Coordinate(C.COORDINATES.indexOf(s.toUpperCase().substr(0,1)),
      this.height - parseInt(s.substr(1)));
};

/**
 * Make a human readable "J18" type string representation of the coordinate.
 *
 * @param {Coordinate} c Coordinate.
 * @returns {string} representation.
 */
Board.prototype.toString = function(c) {
  return C.COORDINATES[c.i] + (this.height-c.j);
};

/**
 * Simple iteration over all coordinates.
 *
 * @param {func} func The iterator method, which is called with the
 * coordinate, type and mark parameters.
 * @param {int} [i1] Column start.
 * @param {int} [j1] Row start.
 * @param {int} [i2] Colunm end.
 * @param {int} [j2] Row end.
 */
Board.prototype.each = function(func, i1, j1, i2, j2) {
  var c = new Coordinate();

  if(i1 === undefined) i1 = 0;
  if(j1 === undefined) j1 = 0;
  if(i2 === undefined) i2 = this.width-1;
  if(j2 === undefined) j2 = this.height-1;

  for(c.j=j1; c.j<=j2; c.j++)
    for(c.i=i1; c.i<=i2; c.i++)
      func(c.copy(), this.stones[c.i][c.j], this.marks[c.i][c.j]);
};

/**
 * Clear board.
 */
Board.prototype.clear = function() {
  this.each(function(c) {
    this.setType(c, C.CLEAR);
    this.setMark(c, C.MARK.NONE);
  }.bind(this));
};

/**
 * Set the intersection type at given coordinate(s).
 *
 * @param {Object} c A Coordinate or Array of them.
 * @param {Object} t New type, e.g. CLEAR, BLACK, ...
 */
Board.prototype.setType = function(c, t) {
  if(c instanceof Coordinate) {
    var old = this.stones[c.i][c.j];

    if(old == t) return; // no change

    this.stones[c.i][c.j] = t;

    var ev = { type: 'type', coordinate: c, board: this,
      oldVal: old, newVal: t };
    this.listeners.forEach(function(l) { l(ev); });
  } else if(c instanceof Array) {
    for(var i=0, len=c.length; i<len; ++i)
      this.setType(c[i], t); // use ourself to avoid duplicate code
  }
};


/**
 * Set the intersection mark at given coordinate(s).
 *
 * @param {Object} c A Coordinate or Array of them.
 * @param {Object} m New mark, e.g. MARK.NONE, MARK.TRIANGLE, ...
 */
Board.prototype.setMark = function(c, m) {
  if(c instanceof Coordinate) {
    var old = this.marks[c.i][c.j];

    if(old == m) return; // no change

    this.marks[c.i][c.j] = m;

    var ev = { type: 'mark', coordinate: c, board: this,
      oldVal: old, newVal: m };
    this.listeners.forEach(function(l) { l(ev); });
  } else if(c instanceof Array) {
    for(var i=0, len=c.length; i<len; ++i)
      this.setMark(c[i], m); // use ourself to avoid duplicate code
  }
};

/**
 * Get the intersection type(s) at given coordinate(s).
 *
 * @param {Object} c A Coordinate or an Array of them.
 * @returns {Object} Type or array of types.
 */
Board.prototype.getType = function(c) {
  var ret;

  if(c instanceof Coordinate) {
    ret = this.stones[c.i][c.j];
  } else if(c instanceof Array) {
    ret = [];
    for(var i=0, len=c.length; i<len; ++i)
      ret.push(this.stones[c[i].i][c[i].j]);
  }

  return ret;
};

/**
 * Get the intersection mark(s) at given coordinate(s).
 *
 * @param {Object} c A Coordinate or an Array of them.
 * @returns {Object} Mark or array of marks.
 */
Board.prototype.getMark = function(c) {
  var ret;

  if(c instanceof Coordinate) {
    ret = this.marks[c.i][c.j];
  } else if(c instanceof Array) {
    ret = [];
    for(var i=0, len=c.length; i<len; ++i)
      ret.push(this.marks[c[i].i][c[i].j]);
  }

  return ret;
};

/**
 * Get neighboring coordinates on board.
 *
 * @param {Coordinate} c The coordinate
 * @returns {Array} The array of adjacent coordinates (2-4)
 */
Board.prototype.getAdjacent = function(c) {
  var coordinates = [], i = c.i, j = c.j;

  if(i>0)
    coordinates.push(new Coordinate(i-1, j));
  if(i+1<this.width)
    coordinates.push(new Coordinate(i+1, j));
  if(j>0)
    coordinates.push(new Coordinate(i, j-1));
  if(j+1<this.height)
    coordinates.push(new Coordinate(i, j+1));

  return coordinates;
};

/**
 * Filter coordinates based on intersection type.
 *
 * @param {Object} c An array of Coordinates.
 * @param {Object} t A type filter (return only matching type).
 * @returns {Object} Object with attributes 'type' and 'mark', array or false.
 */
Board.prototype.filter = function(c, t) {
  var ret = [];
  for(var i=0, len=c.length; i<len; ++i)
    if(this.stones[c[i].i][c[i].j] == t)
      ret.push(c[i]);
  return ret;
};

/**
 * Check if coordinates contain given type.
 *
 * @param {Object} c An array of Coordinates.
 * @param {Object} t A type filter (return only matching type).
 * @returns {bool} True or false.
 */
Board.prototype.hasType = function(c, t) {
  for(var i=0, len=c.length; i<len; ++i)
    if(this.stones[c[i].i][c[i].j] == t)
      return true;
  return false;
};

/**
 * Search all intersections of similar type, return group and edge coordinates.
 *
 * @param {Coordinate} coord The coordinate from which to start search.
 * @param {int} [overrideType] Treat current coordinate as this type.
 * @returns {Object} Two arrays of coordinates in members 'group' and 'neighbors'.
 */
Board.prototype.getGroup = function(coord, overrideType) {
  var type = overrideType || this.getType(coord), seen = {},
      group = [coord.copy()], neighbors = [],
      queue = this.getAdjacent(coord);

  seen[coord.toString()] = true;

  while(queue.length) {
    var c = queue.shift();

    if(c.toString() in seen)
      continue; // seen already
    else
      seen[c.toString()] = true; // seen now

    if(this.getType(c) == type) { // check if type is correct
      group.push(c);
      queue = queue.concat(this.getAdjacent(c)); // add prospects
    } else
      neighbors.push(c);
  }

  return {group: group, neighbors: neighbors};
};

/**
 * Get a raw copy of board contents. Will not include any listeners!
 *
 * @returns {Object} Board contents.
 */
Board.prototype.getRaw = function() {
  return {
    width: this.width,
      height: this.height,
      stones: util.extend({}, this.stones),
      marks: util.extend({}, this.marks)
  };
};

/**
 * Set a raw copy of board contents. Will not change or call any listeners!
 *
 * @param {Object} raw Board contents.
 */
Board.prototype.setRaw = function(raw) {
  this.width = raw.width;
  this.height = raw.height;
  this.stones = raw.stones;
  this.marks = raw.marks;
};

/**
 * Clone a board. This will only copy stones and marks, not listeners!
 *
 * @returns {Object} Cloned board.
 */
Board.prototype.clone = function() {
  var board = new Board();
  board.setRaw(this.getRaw());
  return board;
};

/**
 * Calculate impact of a move on board. Returns a data structure outlining
 * validness of move (success & errorMsg) and possible captures and ko
 * coordinate.
 *
 * @param {Board} jboard Board to play the move on (stays unchanged).
 * @param {Coordinate} coord Coordinate to play or null for pass.
 * @param {int} stone Stone to play - BLACK or WHITE.
 * @param {Coordinate} [ko] Coordinate of previous ko.
 * @returns {Object} Move result data structure.
 */
Board.prototype.playMove = function(coord, stone, ko) {
  var oppType = (stone == C.BLACK ? C.WHITE : C.BLACK),
      captures = [], adjacent, captured = {};

  if(!coord) // pass
    return { success: true, captures: [], ko: false };

  if(this.getType(coord) != C.CLEAR)
    return { success: false,
      errorMsg: 'Cannot play on existing stone!' };

  if(ko && coord.equals(ko))
    return { success: false,
      errorMsg: 'Cannot retake ko immediately!' };

  adjacent = this.getAdjacent(coord); // find adjacent coordinates

  for(var i=0; i<adjacent.length; i++) {
    var c = adjacent[i];
    if(c.toString() in captured) continue; // avoid double capture

    if(this.getType(c) == oppType) { // potential capture
      var g = this.getGroup(c);

      if(this.filter(g.neighbors, C.CLEAR).length === 1) {
        captures = captures.concat(g.group);
        // save captured coordinates so we don't capture them twice
        for(var j=0; j<g.group.length; j++)
          captured[g.group[j].toString()] = true; 
      }
    }
  }

  // Suicide not allowed
  if(captures.length === 0 &&
      !this.hasType(this.getGroup(coord, stone).neighbors, C.CLEAR))
    return { success: false,
      errorMsg: 'Suicide is not allowed!' };

  // Check for ko. Note that captures were not removed so there should
  // be zero liberties around this stone in case of a ko. Also, if the
  // adjacent intersections contain stones of same color, it is not ko.
  if(captures.length == 1 && this.filter(adjacent, C.CLEAR).length === 0
      && this.filter(adjacent, stone).length === 0)
    return { success: true, captures: captures, ko: captures[0].copy() };

  return { success: true, captures: captures, ko: false };
};

module.exports = Board;
