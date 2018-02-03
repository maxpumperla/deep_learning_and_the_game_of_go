(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

//var request = require('superagent');
var C = require('./constants');

/**
 * Automatic div module.
 * @module autodiv
 */

function parseMarkup(str) {
  var lines = str.split('\n'), data = [];

  // Handle div contents as diagram contents
  for(var i = 0, len = lines.length; i < len; ++i) {
    var elems = [], line = lines[i];

    for(var j = 0, len2 = line.length; j < len2; ++j) {
      switch(line[j]) {
        case '.':
          elems.push({type: C.CLEAR}); break;
        case 'o':
          elems.push({type: C.WHITE}); break;
        case 'x':
          elems.push({type: C.BLACK}); break;
        case ' ':
          break; // ignore whitespace
        default: // assume marker
          if(!elems.length) break; // no intersection yet
          // Append to mark so x123 etc. are possible
          if(elems[elems.length - 1].mark)
            elems[elems.length - 1].mark += line[j];
          else
            elems[elems.length - 1].mark = line[j];
      }
    }

    if(elems.length) data.push(elems);
  }

  return data;
}

// Array of loaded boards
//var boards = [];

// Available attributes:
// data-jgostyle: Evaluated and used as board style
// data-jgosize: Used as board size unless data-jgosgf is defined
// data-jgoview: Used to define viewport
function process(JGO, div) {
  // Handle special jgo-* attributes
  var style, width, height, TL, BR; // last two are viewport

  if(div.getAttribute('data-jgostyle')) {
    /*jshint evil:true  */
    style = eval(div.getAttribute('data-jgostyle'));
  } else style = JGO.BOARD.medium;

  if(div.getAttribute('data-jgosize')) {
    var size = div.getAttribute('data-jgosize');

    if(size.indexOf('x') != -1) {
      width = parseInt(size.substring(0, size.indexOf('x')));
      height = parseInt(size.substr(size.indexOf('x')+1));
    } else width = height = parseInt(size);
  }

  //if(div.getAttribute('data-jgosgf'))

  var data = parseMarkup(div.innerHTML);
  div.innerHTML = '';

  if(!width) { // Size still missing
    if(!data.length) return; // no size or data, no board

    height = data.length;
    width = data[0].length;
  }

  var jboard = new JGO.Board(width, height);
  var jsetup = new JGO.Setup(jboard, style);

  if(div.getAttribute('data-jgoview')) {
    var tup = div.getAttribute('data-jgoview').split('-');
    TL = jboard.getCoordinate(tup[0]);
    BR = jboard.getCoordinate(tup[1]);
  } else {
    TL = new JGO.Coordinate(0,0);
    BR = new JGO.Coordinate(width-1, height-1);
  }

  jsetup.view(TL.i, TL.j, width-TL.i, height-TL.j);

  var c = new JGO.Coordinate();

  for(c.j = TL.j; c.j <= BR.j; ++c.j) {
    for(c.i = TL.i; c.i <= BR.i; ++c.i) {
      var elem = data[c.j - TL.j][c.i - TL.i];
      jboard.setType(c, elem.type);
      if(elem.mark) jboard.setMark(c, elem.mark);
    }
  }

  jsetup.create(div);
}

/**
 * Find all div elements with class 'jgoboard' and initialize them.
 */
exports.init = function(document, JGO) {
  var matches = document.querySelectorAll('div.jgoboard');

  for(var i = 0, len = matches.length; i < len; ++i)
    process(JGO, matches[i]);
};

},{"./constants":4}],2:[function(require,module,exports){
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

},{"./constants":4,"./coordinate":5,"./util":13}],3:[function(require,module,exports){
'use strict';

var C = require('./constants');
var Coordinate = require('./coordinate');
var Stones = require('./stones');
var util = require('./util');

/**
 * Create a jGoBoard canvas object.
 *
 * @param {Object} elem Container HTML element or its id.
 * @param {Object} opt Options object.
 * @param {Object} images Set of images (or false values) for drawing.
 * @constructor
 */
var Canvas = function(elem, opt, images) {
  /* global document */
  if(typeof elem === 'string')
    elem = document.getElementById(elem);

  var canvas = document.createElement('canvas'), i, j;

  var padLeft = opt.edge.left ? opt.padding.normal : opt.padding.clipped,
      padRight = opt.edge.right ? opt.padding.normal : opt.padding.clipped,
      padTop = opt.edge.top ? opt.padding.normal : opt.padding.clipped,
      padBottom = opt.edge.bottom ? opt.padding.normal : opt.padding.clipped;

  this.marginLeft = opt.edge.left ? opt.margin.normal : opt.margin.clipped;
  this.marginRight = opt.edge.right ? opt.margin.normal : opt.margin.clipped;
  this.marginTop = opt.edge.top ? opt.margin.normal : opt.margin.clipped;
  this.marginBottom = opt.edge.bottom ? opt.margin.normal : opt.margin.clipped;

  this.boardWidth = padLeft + padRight +
    opt.grid.x * opt.view.width;
  this.boardHeight = padTop + padBottom +
    opt.grid.y * opt.view.height;

  this.width = canvas.width =
    this.marginLeft + this.marginRight + this.boardWidth;
  this.height = canvas.height =
    this.marginTop + this.marginBottom + this.boardHeight;

  this.listeners = {'click': [], 'mousemove': [], 'mouseout': []};

  /**
   * Get board coordinate based on screen coordinates.
   * @param {number} x Coordinate.
   * @param {number} y Coordinate.
   * @returns {Coordinate} Board coordinate.
   */
  this.getCoordinate = function(pageX, pageY) {
    var bounds = canvas.getBoundingClientRect(),
        scaledX = (pageX - bounds.left) * canvas.width / (bounds.right - bounds.left),
        scaledY = (pageY - bounds.top) * canvas.height / (bounds.bottom - bounds.top);

    return new Coordinate(
        Math.floor((scaledX-this.marginLeft-padLeft)/opt.grid.x) + opt.view.xOffset,
        Math.floor((scaledY-this.marginTop-padTop)/opt.grid.y) + opt.view.yOffset);
  }.bind(this);

  // Click handler will call all listeners passing the coordinate of click
  // and the click event
  canvas.onclick = function(ev) {
    var c = this.getCoordinate(ev.clientX, ev.clientY),
        listeners = this.listeners.click;

    for(var l=0; l<listeners.length; l++)
      listeners[l].call(this, c.copy(), ev);
  }.bind(this);

  var lastMove = new Coordinate(-1,-1);

  // Move handler will call all listeners passing the coordinate of move
  // whenever mouse moves over a new intersection
  canvas.onmousemove = function(ev) {
    if(!this.listeners.mousemove.length) return;

    var c = this.getCoordinate(ev.clientX, ev.clientY),
        listeners = this.listeners.mousemove;

    if(c.i < this.opt.view.xOffset ||
        c.i >= this.opt.view.xOffset + this.opt.view.width)
      c.i = -1;

    if(c.j < this.opt.view.yOffset ||
        c.j >= this.opt.view.yOffset + this.opt.view.height)
      c.j = -1;

    if(lastMove.equals(c))
      return; // no change
    else
      lastMove = c.copy();

    for(var l=0; l<listeners.length; l++)
      listeners[l].call(this, c.copy(), ev);
  }.bind(this);

  // Mouseout handler will again call all listeners of that event, no
  // coordinates will be passed of course, only the event
  canvas.onmouseout = function(ev) {
    var listeners = this.listeners.mouseout;

    for(var l=0; l<listeners.length; l++)
      listeners[l].call(this, ev);
  }.bind(this);

  elem.appendChild(canvas);

  this.ctx = canvas.getContext('2d');
  this.opt = util.extend({}, opt); // make a copy just in case
  this.stones = new Stones(opt, images);
  this.images = images;

  // Fill margin with correct color
  this.ctx.fillStyle = opt.margin.color;
  this.ctx.fillRect(0, 0, canvas.width, canvas.height);

  if(this.images.board) {
    // Prepare to draw board with shadow
    this.ctx.save();
    this.ctx.shadowColor = opt.boardShadow.color;
    this.ctx.shadowBlur = opt.boardShadow.blur;
    this.ctx.shadowOffsetX = opt.boardShadow.offX;
    this.ctx.shadowOffsetX = opt.boardShadow.offY;

    var clipTop = opt.edge.top ? 0 : this.marginTop,
        clipLeft = opt.edge.left ? 0 : this.marginLeft,
        clipBottom = opt.edge.bottom ? 0 : this.marginBottom,
        clipRight = opt.edge.right ? 0 : this.marginRight;

    // Set clipping to throw shadow only on actual edges
    this.ctx.beginPath();
    this.ctx.rect(clipLeft, clipTop,
        canvas.width - clipLeft - clipRight,
        canvas.height - clipTop - clipBottom);
    this.ctx.clip();

    this.ctx.drawImage(this.images.board, 0, 0,
        this.boardWidth, this.boardHeight,
        this.marginLeft, this.marginTop,
        this.boardWidth, this.boardHeight);

    // Draw lighter border around the board to make it more photography
    this.ctx.strokeStyle = opt.border.color;
    this.ctx.lineWidth = opt.border.lineWidth;
    this.ctx.beginPath();
    this.ctx.rect(this.marginLeft, this.marginTop,
        this.boardWidth, this.boardHeight);
    this.ctx.stroke();

    this.ctx.restore(); // forget shadow and clipping
  }

  // Top left center of grid (not edge, center!)
  this.gridTop = this.marginTop + padTop + opt.grid.y / 2;
  this.gridLeft = this.marginLeft + padLeft + opt.grid.x / 2;

  this.ctx.strokeStyle = opt.grid.color;

  var smt = this.opt.grid.smooth; // with 0.5 there will be full antialias

  // Draw vertical gridlines
  for(i=0; i<opt.view.width; i++) {
    if((i === 0 && opt.edge.left) || (i+1 == opt.view.width && opt.edge.right))
      this.ctx.lineWidth = opt.grid.borderWidth;
    else
      this.ctx.lineWidth = opt.grid.lineWidth;

    this.ctx.beginPath();

    this.ctx.moveTo(smt + this.gridLeft + opt.grid.x * i,
        smt + this.gridTop - (opt.edge.top ? 0 : opt.grid.y / 2 + padTop/2));
    this.ctx.lineTo(smt + this.gridLeft + opt.grid.x * i,
        smt + this.gridTop + opt.grid.y * (opt.view.height - 1) +
        (opt.edge.bottom ? 0 : opt.grid.y / 2 + padBottom/2));
    this.ctx.stroke();
  }

  // Draw horizontal gridlines
  for(i=0; i<opt.view.height; i++) {
    if((i === 0 && opt.edge.top) || (i+1 == opt.view.height && opt.edge.bottom))
      this.ctx.lineWidth = opt.grid.borderWidth;
    else
      this.ctx.lineWidth = opt.grid.lineWidth;

    this.ctx.beginPath();

    this.ctx.moveTo(smt + this.gridLeft - (opt.edge.left ? 0 : opt.grid.x / 2 + padLeft/2),
        smt + this.gridTop + opt.grid.y * i);
    this.ctx.lineTo(smt + this.gridLeft + opt.grid.x * (opt.view.width - 1) +
        (opt.edge.right ? 0 : opt.grid.x / 2 + padRight/2),
        smt + this.gridTop + opt.grid.y * i);
    this.ctx.stroke();
  }

  if(opt.stars.points) { // If star points
    var step = (opt.board.width - 1) / 2 - opt.stars.offset;
    // 1, 4, 5, 8 and 9 points are supported, rest will result in randomness
    for(j=0; j<3; j++) {
      for(i=0; i<3; i++) {
        if(j == 1 && i == 1) { // center
          if(opt.stars.points % 2 === 0)
            continue; // skip center
        } else if(i == 1 || j == 1) { // non-corners
          if(opt.stars.points < 8)
            continue; // skip non-corners
        } else { // corners
          if(opt.stars.points < 4)
            continue; // skip corners
        }

        var x = (opt.stars.offset + i * step) - opt.view.xOffset,
            y = (opt.stars.offset + j * step) - opt.view.yOffset;

        if(x < 0 || y < 0 || x >= opt.view.width || y >= opt.view.height)
          continue; // invisible

        this.ctx.beginPath();
        this.ctx.arc(smt + this.gridLeft + x * opt.grid.x,
            smt + this.gridTop + y * opt.grid.y,
            opt.stars.radius, 2*Math.PI, false);
        this.ctx.fillStyle = opt.grid.color;
        this.ctx.fill();
      }
    }
  }

  this.ctx.font = opt.coordinates.font;
  this.ctx.fillStyle = opt.coordinates.color;
  this.ctx.textAlign = 'center';
  this.ctx.textBaseline = 'middle';

  // Draw horizontal coordinates
  for(i=0; i<opt.view.width; i++) {
    if(opt.coordinates && opt.coordinates.top)
      this.ctx.fillText(C.COORDINATES[i + opt.view.xOffset],
          this.gridLeft + opt.grid.x * i,
          this.marginTop / 2);
    if(opt.coordinates && opt.coordinates.bottom)
      this.ctx.fillText(C.COORDINATES[i + opt.view.xOffset],
          this.gridLeft + opt.grid.x * i,
          canvas.height - this.marginBottom / 2);
  }

  // Draw vertical coordinates
  for(i=0; i<opt.view.height; i++) {
    if(opt.coordinates && opt.coordinates.left)
      this.ctx.fillText(''+(opt.board.height-opt.view.yOffset-i),
          this.marginLeft / 2,
          this.gridTop + opt.grid.y * i);
    if(opt.coordinates && opt.coordinates.right)
      this.ctx.fillText(''+(opt.board.height-opt.view.yOffset-i),
          canvas.width - this.marginRight / 2,
          this.gridTop + opt.grid.y * i);
  }

  // Store rendered board in another canvas for fast redraw
  this.backup = document.createElement('canvas');
  this.backup.width = canvas.width;
  this.backup.height = canvas.height;
  this.backup.getContext('2d').drawImage(canvas,
      0, 0, canvas.width, canvas.height,
      0, 0, canvas.width, canvas.height);


  // Clip further drawing to board only
  this.ctx.beginPath();
  this.ctx.rect(this.marginLeft, this.marginTop, this.boardWidth, this.boardHeight);
  this.ctx.clip();

  // Fix Chromium bug with image glitches unless they are drawn once
  // https://code.google.com/p/chromium/issues/detail?id=469906
  if(this.images.black) this.ctx.drawImage(this.images.black, 10, 10);
  if(this.images.white) this.ctx.drawImage(this.images.white, 10, 10);
  if(this.images.shadow) this.ctx.drawImage(this.images.shadow, 10, 10);
  // Sucks but works
  this.restore(this.marginLeft, this.marginTop, this.boardWidth, this.boardHeight);
};

/**
 * Restore portion of canvas.
 */
Canvas.prototype.restore = function(x, y, w, h) {
  x = Math.floor(x);
  y = Math.floor(y);
  x = Math.max(x, 0);
  y = Math.max(y, 0);
  w = Math.min(w, this.backup.width - x);
  h = Math.min(h, this.backup.height - y);
  try {
    this.ctx.drawImage(this.backup, x, y, w, h, x, y, w, h);
  }
  catch (e) {
    console.log(e);
  }
};

/**
 * Get X coordinate based on column.
 * @returns {number} Coordinate.
 */
Canvas.prototype.getX = function(i) {
  return this.gridLeft + this.opt.grid.x * i;
};

/**
 * Get Y coordinate based on row.
 * @returns {number} Coordinate.
 */
Canvas.prototype.getY = function(j) {
  return this.gridTop + this.opt.grid.y * j;
};

/**
 * Redraw canvas portion using a board.
 *
 * @param {Board} jboard Board object.
 * @param {number} i1 Starting column to be redrawn.
 * @param {number} j1 Starting row to be redrawn.
 * @param {number} i2 Ending column to be redrawn (inclusive).
 * @param {number} j2 Ending row to be redrawn (inclusive).
 */
Canvas.prototype.draw = function(jboard, i1, j1, i2, j2) {
  i1 = Math.max(i1, this.opt.view.xOffset);
  j1 = Math.max(j1, this.opt.view.yOffset);
  i2 = Math.min(i2, this.opt.view.xOffset + this.opt.view.width - 1);
  j2 = Math.min(j2, this.opt.view.yOffset + this.opt.view.height - 1);

  if(i2 < i1 || j2 < j1)
    return; // nothing to do here

  var x = this.getX(i1 - this.opt.view.xOffset) - this.opt.grid.x,
      y = this.getY(j1 - this.opt.view.yOffset) - this.opt.grid.y,
      w = this.opt.grid.x * (i2 - i1 + 2),
      h = this.opt.grid.y * (j2 - j1 + 2);

  this.ctx.save();
  this.ctx.beginPath();
  this.ctx.rect(x, y, w, h);
  this.ctx.clip(); // only apply redraw to relevant area
  this.restore(x, y, w, h); // restore background

  // Expand redrawn intersections while keeping within viewport
  i1 = Math.max(i1-1, this.opt.view.xOffset);
  j1 = Math.max(j1-1, this.opt.view.yOffset);
  i2 = Math.min(i2+1, this.opt.view.xOffset + this.opt.view.width - 1);
  j2 = Math.min(j2+1, this.opt.view.yOffset + this.opt.view.height - 1);

  var isLabel = /^[a-zA-Z1-9]/;

  // Stone radius derived marker size parameters
  var stoneR = this.opt.stone.radius,
      clearW = stoneR * 1.5, clearH = stoneR * 1.2, clearFunc;

  // Clear grid for labels on clear intersections before casting shadows
  if(this.images.board) { // there is a board texture
    clearFunc = function(ox, oy) {
      this.ctx.drawImage(this.images.board,
          ox - this.marginLeft - clearW / 2, oy - this.marginTop - clearH / 2, clearW, clearH,
          ox - clearW / 2, oy - clearH / 2, clearW, clearH);
    }.bind(this);
  } else { // no board texture
    this.ctx.fillStyle = this.opt.margin.color;
    clearFunc = function(ox, oy) {
      this.ctx.fillRect(ox - clearW / 2, oy - clearH / 2, clearW, clearH);
    }.bind(this);
  }

  // Clear board grid under markers when needed
  jboard.each(function(c, type, mark) {
    // Note: Use of smt has been disabled here for clear results
    var ox = this.getX(c.i - this.opt.view.xOffset);
    var oy = this.getY(c.j - this.opt.view.yOffset);

    if(type == C.CLEAR && mark && isLabel.test(mark))
    clearFunc(ox, oy);
  }.bind(this), i1, j1, i2, j2); // provide iteration limits

  // Shadows
  jboard.each(function(c, type) {
    var ox = this.getX(c.i - this.opt.view.xOffset);
    var oy = this.getY(c.j - this.opt.view.yOffset);

    if(type == C.BLACK || type == C.WHITE) {
      this.stones.drawShadow(this.ctx,
          this.opt.shadow.xOff + ox,
          this.opt.shadow.yOff + oy);
    }
  }.bind(this), i1, j1, i2, j2); // provide iteration limits

  // Stones and marks
  jboard.each(function(c, type, mark) {
    var ox = (this.getX(c.i - this.opt.view.xOffset));
    var oy = (this.getY(c.j - this.opt.view.yOffset));
    var markColor;

    switch(type) {
      case C.BLACK:
      case C.DIM_BLACK:
        this.ctx.globalAlpha = type == C.BLACK ? 1 : this.opt.stone.dimAlpha;
        this.stones.drawStone(this.ctx, type, ox, oy);
        markColor = this.opt.mark.blackColor; // if we have marks, this is the color
        break;
      case C.WHITE:
      case C.DIM_WHITE:
        this.ctx.globalAlpha = type == C.WHITE ? 1 : this.opt.stone.dimAlpha;
        this.stones.drawStone(this.ctx, type, ox, oy);
        markColor = this.opt.mark.whiteColor; // if we have marks, this is the color
        break;
      default:
        this.ctx.globalAlpha=1;
        markColor = this.opt.mark.clearColor; // if we have marks, this is the color
    }

    // Common settings to all markers
    this.ctx.lineWidth = this.opt.mark.lineWidth;
    this.ctx.strokeStyle = markColor;

    this.ctx.font = this.opt.mark.font;
    this.ctx.fillStyle = markColor;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';

    if(mark) this.stones.drawMark(this.ctx, mark, ox, oy);
  }.bind(this), i1, j1, i2, j2); // provide iteration limits

  this.ctx.restore(); // also restores globalAlpha
};

/**
 * Add an event listener to canvas (click) events. The callback will be
 * called with 'this' referring to Canvas object, with coordinate and
 * event as parameters. Supported event types are 'click', 'mousemove',
 * and 'mouseout'. With 'mouseout', there is no coordinate parameter for
 * callback.
 *
 * @param {String} event The event to listen to, e.g. 'click'.
 * @param {function} callback The callback.
 */
Canvas.prototype.addListener = function(event, callback) {
  this.listeners[event].push(callback);
};

module.exports = Canvas;

},{"./constants":4,"./coordinate":5,"./stones":12,"./util":13}],4:[function(require,module,exports){
'use strict';

var util = require('./util');

/**
 * Enum for intersection types. Aliased in JGO namespace, e.g. JGO.BLACK.
 * @enum
 * @readonly
 */
exports.INTERSECTION = {
  CLEAR: 0,
  /** Black stone */
  BLACK: 1,
  /** White stone */
  WHITE: 2,
  /** Semi-transparent black stone */
  DIM_BLACK: 3,
  /** Semi-transparent white stone */
  DIM_WHITE: 4
};

// Alias all objects into globals
util.extend(exports, exports.INTERSECTION);

/**
 * Enum for marker types.
 * @readonly
 * @enum
 */
exports.MARK = {
  /** No marker ('') */
  NONE: '',
  /** Selected intersection */
  SELECTED: '^',
  /** Square */
  SQUARE: '#',
  /** Triangle */
  TRIANGLE: '/',
  /** Circle */
  CIRCLE: '0',
  /** Cross */
  CROSS: '*',
  /** Black territory */
  BLACK_TERRITORY: '-',
  /** White territory */
  WHITE_TERRITORY: '+'
};

/**
 * Board coordinate array.
 * @constant
 */
exports.COORDINATES = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'.split('');

},{"./util":13}],5:[function(require,module,exports){
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

},{}],6:[function(require,module,exports){
'use strict';

var JGO = require('./constants'); // base for JGO object

JGO.Coordinate = require('./coordinate');
JGO.Canvas = require('./canvas');
JGO.Node = require('./node');
JGO.Notifier = require('./notifier');
JGO.Record = require('./record');
JGO.Setup = require('./setup');
JGO.Stones = require('./stones');
JGO.Board = require('./board');
JGO.util = require('./util');
JGO.sgf = require('./sgf');
JGO.auto = require('./auto');

module.exports = JGO;

},{"./auto":1,"./board":2,"./canvas":3,"./constants":4,"./coordinate":5,"./node":7,"./notifier":8,"./record":9,"./setup":10,"./sgf":11,"./stones":12,"./util":13}],7:[function(require,module,exports){
'use strict';

var util = require('./util');
var C = require('./constants');

/**
 * Helper class to store node information, apply and revert changes easily.
 *
 * @param {Board} jboard Board object to make changes on.
 * @param {Node} parent Parent node or null if no parent.
 * @param {Object} info Node information - ko coordinate, comment, etc.
 * @constructor
 */
var Node = function(jboard, parent, info) {
  this.jboard = jboard;
  this.parent = parent;
  this.info = info ? util.extend({}, info) : {};
  this.children = [];
  this.changes = [];

  if(parent) {
    parent.children.push(this); // register child
    this.info.captures = util.extend({}, parent.info.captures);
  } else {
    this.info.captures = {1: 0, 2: 0}; // C.BLACK, C.WHITE
  }
};

/**
 * Helper method to clear parent node's markers. Created to achieve SGF like
 * stateless marker behavaior.
 */
Node.prototype.clearParentMarks = function() {
  if(!this.parent)
    return;

  for(var i=this.parent.changes.length-1; i>=0; i--) {
    var item = this.parent.changes[i];

    if('mark' in item)
      this.setMark(item.c, C.MARK.NONE);
  }
};

/**
 * Helper method to make changes to a board while saving them in the node.
 *
 * @param {Object} c Coordinate or array of them.
 * @param {int} val Type.
 */
Node.prototype.setType = function(c, val) {
  if(c instanceof Array) {
    for(var i=0, len=c.length; i<len; ++i)
      this.setType(c[i], val); // avoid repeating ourselves
    return;
  }

  // Store both change and previous value to enable reversion
  this.changes.push({c: c.copy(), type: val, old: this.jboard.getType(c)});
  this.jboard.setType(c, val);
};

/**
 * Helper method to make changes to a board while saving them in the node.
 *
 * @param {Object} c Coordinate or array of them.
 * @param {int} val Mark.
 */
Node.prototype.setMark = function(c, val) {
  if(c instanceof Array) {
    for(var i=0, len=c.length; i<len; ++i)
      this.setMark(c[i], val); // avoid repeating ourselves
    return;
  }

  // Store both change and previous value to enable reversion
  this.changes.push({c: c.copy(), mark: val, old: this.jboard.getMark(c)});
  this.jboard.setMark(c, val);
};


/**
 * Apply changes of this node to board.
 */
Node.prototype.apply = function() {
  for(var i=0; i<this.changes.length; i++) {
    var item = this.changes[i];

    if('type' in item)
      this.jboard.setType(item.c, item.type);
    else
      this.jboard.setMark(item.c, item.mark);
  }
};

/**
 * Revert changes of this node to board.
 */
Node.prototype.revert = function() {
  for(var i=this.changes.length-1; i>=0; i--) {
    var item = this.changes[i];

    if('type' in item)
      this.jboard.setType(item.c, item.old);
    else
      this.jboard.setMark(item.c, item.old);
  }
};

module.exports = Node;

},{"./constants":4,"./util":13}],8:[function(require,module,exports){
'use strict';

/**
 * A change notifier class that can listen to changes in a Board and keep
 * multiple Canvas board views up to date.
 *
 * @param {Board} jboard The board to listen to.
 * @constructor
 */
var Notifier = function(jboard) {
  this.updateScheduled = false; // set on first change
  this.canvases = []; // canvases to notify on changes
  this.board = jboard;

  this.changeFunc = function(ev) {
    var coord = ev.coordinate;

    if(this.updateScheduled) { // update already scheduled
      this.min.i = Math.min(this.min.i, coord.i);
      this.min.j = Math.min(this.min.j, coord.j);
      this.max.i = Math.max(this.max.i, coord.i);
      this.max.j = Math.max(this.max.j, coord.j);
      return;
    }

    this.min = coord.copy();
    this.max = coord.copy();
    this.updateScheduled = true;

    setTimeout(function() { // schedule update in the end
      for(var c=0; c<this.canvases.length; c++)
        this.canvases[c].draw(this.board, this.min.i, this.min.j,
          this.max.i, this.max.j);

      this.updateScheduled = false; // changes updated, scheduled function run
    }.bind(this), 0);
  }.bind(this);

  this.board.addListener(this.changeFunc);
};

/**
 * Change the board to listen to. Notifier will stop listening previous board,
 * start listening new one and trigger full redraw of canvas.
 *
 * @param {Board} board New board to listen to.
 */
Notifier.prototype.changeBoard = function(board) {
  this.board.removeListener(this.changeFunc);
  this.board = board;
  this.board.addListener(this.changeFunc);
  // There might be a scheduled update timeout, but ignore that, it will
  // just redraw a portion of new board
  for(var c=0; c<this.canvases.length; c++)
    this.canvases[c].draw(this.board, 0, 0, this.board.width, this.board.height);
};

/**
 * Add a canvas to notify list.
 *
 * @param {Canvas} jcanvas The canvas to add.
 */
Notifier.prototype.addCanvas = function(jcanvas) {
  this.canvases.push(jcanvas);
};

module.exports = Notifier;

},{}],9:[function(require,module,exports){
'use strict';

var Board = require('./board');
var Node = require('./node');

/**
 * Create a go game record that can handle plays and variations. A Board
 * object is created that will reflect the current position in game record.
 *
 * @param {int} width Board width.
 * @param {int} height Board height.
 * @constructor
 */
var Record = function(width, height) {
  this.jboard = new Board(width, height ? height : width);
  this.root = this.current = null;
  this.info = {}; // game information
};

/**
 * Get board object.
 *
 * @returns {Board} Board object.
 */
Record.prototype.getBoard = function() {
  return this.jboard;
};

/**
 * Get current node.
 *
 * @returns {Node} Current node.
 */
Record.prototype.getCurrentNode = function() {
  return this.current;
};


/**
 * Get root node.
 *
 * @returns {Node} Root node.
 */
Record.prototype.getRootNode = function() {
  return this.root;
};

/**
 * Create new empty node under current one.
 *
 * @param {bool} clearParentMarks True to clear parent node marks.
 * @param {Object} info Node information - ko coordinate, comment, etc.
 * @returns {Node} New, current node.
 */
Record.prototype.createNode = function(clearParentMarks, options) {
  var node = new Node(this.jboard, this.current, options);

  if(clearParentMarks)
    node.clearParentMarks();

  if(this.root === null)
    this.root = node;

  return (this.current = node);
};

/**
 * Advance to the next node in the game tree.
 *
 * @param {int} [variation] parameter to specify which variation to select, if there are several branches.
 * @returns {Node} New current node or null if at the end of game tree.
 */
Record.prototype.next = function(variation) {
  if(this.current === null)
    return null;

  if(!variation)
    variation = 0;

  if(variation >= this.current.children.length)
    return null;

  this.current = this.current.children[variation];
  this.current.apply(this.jboard);

  return this.current;
};

/**
 * Back up a node in the game tree.
 *
 * @returns {Node} New current node or null if at the beginning of game tree.
 */
Record.prototype.previous = function() {
  if(this.current === null || this.current.parent === null)
    return null; // empty or no parent

  this.current.revert(this.jboard);
  this.current = this.current.parent;

  return this.current;
};

/**
 * Get current variation number (zero-based).
 *
 * @returns {int} Current variations.
 */
Record.prototype.getVariation = function() {
  if(this.current === null || this.current.parent === null)
    return 0;
  return this.current.parent.children.indexOf(this.current);
};

/**
 * Go to a variation. Uses previous() and next().
 *
 * @param {int} [variation] parameter to specify which variation to select, if there are several branches.
 */
Record.prototype.setVariation = function(variation) {
  if(this.previous() === null)
    return null;
  return this.next(variation);
};

/**
 * Get number of variations for current node.
 *
 * @returns {int} Number of variations.
 */
Record.prototype.getVariations = function() {
  if(this.current === null || this.current.parent === null)
    return 1;

  return this.current.parent.children.length; // "nice"
};

/**
 * Go to the beginning of the game tree.
 *
 * @returns {Node} New current node.
 */
Record.prototype.first = function() {
  this.current = this.root;
  this.jboard.clear();

  if(this.current !== null)
    this.current.apply(this.jboard);

  return this.current;
};

/**
 * Create a snapshot of current Record state. Will contain board state and
 * current node.
 *
 * @returns Snapshot to be used with restoreSnapshot().
 */
Record.prototype.createSnapshot = function() {
  return {jboard: this.jboard.getRaw(), current: this.current};
};

/**
 * Restore the Record to the state contained in snapshot. Use only if you
 * REALLY know what you are doing, this is mainly for creating Record
 * quickly from SGF.
 *
 * @param {Object} raw Snapshot created with createSnapshot().
 */
Record.prototype.restoreSnapshot = function(raw) {
  this.jboard.setRaw(raw.jboard);
  this.current = raw.current;
};

/**
 * Normalize record so the longest variation is the first.
 *
 * @param {Node} node The node to start with. Defaults to root if unset.
 * @returns int Length of longest subsequence.
 */
Record.prototype.normalize = function(node) {
  var i, len, maxLen = 0, maxI = 0;

  if(!node) node = this.getRootNode();

  for(i=0; i<node.children.length; i++) {
    len = this.normalize(node.children[i]);
    if(maxLen < len) { maxLen = len; maxI = i; }
  }

  if(maxI) { // If needed, swap longest first
    i = node.children[0];
    node.children[0] = node.children[maxI];
    node.children[maxI] = i;
  }

  return maxLen + 1; // longest subsequence plus this
};

module.exports = Record;

},{"./board":2,"./node":7}],10:[function(require,module,exports){
'use strict';

var Notifier = require('./notifier');
var Canvas = require('./canvas');
var util = require('./util');

/**
 * Setup helper class to make creating Canvases easy.
 *
 * @param {Board} jboard Board object to listen to.
 * @param {Object} boardOptions Base board options like BOARD.large.
 * @constructor
 */
var Setup = function(board, boardOptions) {
  var defaults = {
    margin: {color:'white'},
    edge: {top:true, bottom:true, left:true, right:true},
    coordinates: {top:true, bottom:true, left:true, right:true},
    stars: {points: 0 },
    board: {width:board.width, height:board.height},
    view: {xOffset:0, yOffset:0, width:board.width, height:board.height}
  };

  if(board.width == board.height) {
    switch(board.width) { // square
      case 9:
        defaults.stars.points=5;
        defaults.stars.offset=2;
        break;
      case 13:
      case 19:
        defaults.stars.points=9;
        defaults.stars.offset=3;
        break;
    }
  }

  this.board = board; // board to follow
  this.notifier = new Notifier(this.board); // notifier to canvas
  this.options = util.extend(defaults, boardOptions); // clone
};

/**
 * View only a portion of the whole board.
 *
 * @param {int} xOff The X offset.
 * @param {int} yOff The Y offset.
 * @param {int} width The width.
 * @param {int} height The height.
 */
Setup.prototype.view = function(xOff, yOff, width, height) {
  this.options.view.xOffset = xOff;
  this.options.view.yOffset = yOff;
  this.options.view.width = width;
  this.options.view.height = height;

  this.options.edge.left = (xOff === 0);
  this.options.edge.right = (xOff+width == this.options.board.width);

  this.options.edge.top = (yOff === 0);
  this.options.edge.bottom = (yOff+height == this.options.board.height);
};

/**
 * Replace default options (non-viewport related)
 *
 * @param {Object} options The new options.
 */
Setup.prototype.setOptions = function(options) {
  util.extend(this.options, options);
};

/**
 * Get {@link Notifier} object created by this class. Can be used to
 * change the board the canvas listens to.
 *
 * @returns {Notifier} Canvas notifier.
 */
Setup.prototype.getNotifier = function() {
  return this.notifier;
};

/**
 * Create Canvas based on current settings. When textures are used,
 * image resources need to be loaded, so the function returns and
 * asynchronously call readyFn after actual initialization.
 *
 * @param {Object} elemId The element id or HTML Node where to create the canvas in.
 * @param {function} readyFn Function to call with canvas once it is ready.
 */
Setup.prototype.create = function(elemId, readyFn) {
  var options = util.extend({}, this.options); // create a copy

  var createCallback = function(images) {
    var jcanvas = new Canvas(elemId, options, images);

    jcanvas.draw(this.board, 0, 0, this.board.width-1, this.board.height-1);

    // Track and group later changes with Notifier
    this.notifier.addCanvas(jcanvas);

    if(readyFn) readyFn(jcanvas);
  }.bind(this);

  if(this.options.textures) // at least some textures exist
    util.loadImages(this.options.textures, createCallback);
  else // blain BW board
    createCallback({black:false,white:false,shadow:false,board:false});
};

module.exports = Setup;

},{"./canvas":3,"./notifier":8,"./util":13}],11:[function(require,module,exports){
'use strict';

/**
 * SGF loading module.
 * @module sgf
 */

var Coordinate = require('./coordinate');
var Record = require('./record');
var C = require('./constants');

var ERROR; // error holder for sgfParse etc.

var fieldMap = {
  'AN': 'annotator',
  'CP': 'copyright',
  'DT': 'date',
  'EV': 'event',
  'GN': 'gameName',
  'OT': 'overtime',
  'RO': 'round',
  'RE': 'result',
  'RU': 'rules',
  'SO': 'source',
  'TM': 'time',
  'PC': 'location',
  'PB': 'black',
  'PW': 'white',
  'BR': 'blackRank',
  'WR': 'whiteRank',
  'BT': 'blackTeam',
  'WT': 'whiteTeam'
};

/*
 * Helper function to handle single coordinates as well as coordinate lists.
 *
 * @param {object} propValues A property value array containing a mix of coordinates (aa) and lists (aa:bb)
 * @returns {array} An array of Coordinate objects matching the given property values.
 */
function explodeSGFList(propValues) {
  var coords = [];

  for(var i=0, len=propValues.length; i<len; i++) {
    var val = propValues[i];

    if(val.indexOf(':') == -1) { // single coordinate
      coords.push(new Coordinate(val));
    } else {
      var tuple = val.split(':'), c1, c2, coord;

      c1 = new Coordinate(tuple[0]);
      c2 = new Coordinate(tuple[1]);
      coord = new Coordinate();

      for(coord.i=c1.i; coord.i<=c2.i; ++coord.i)
        for(coord.j=c1.j; coord.j<=c2.j; ++coord.j)
          coords.push(coord.copy());
    }
  }

  return coords;
}

function sgfMove(node, name, values, moveMarks) {
  var coord, player, opponent, play;

  if(name == 'B') {
    player = C.BLACK;
    opponent = C.WHITE;
  } else if('W') {
    player = C.WHITE;
    opponent = C.BLACK;
  }

  coord = (values[0].length == 2) ? new Coordinate(values[0]) : null;

  // Apparently, IGS wants to use outside-board coordinates for pass
  if(coord !== null && (coord.i >= node.jboard.width || coord.j >= node.jboard.height))
    coord = null; // Thank you, IGS

  play = node.jboard.playMove(coord, player);
  node.info.captures[player] += play.captures.length; // tally captures

  if(moveMarks && play.ko)
      node.setMark(play.ko, C.MARK.SQUARE);
  
  if(play.success && coord !== null) {
    node.setType(coord, player); // play stone
    node.setType(play.captures, C.CLEAR); // clear opponent's stones
    if(moveMarks)
      node.setMark(coord, C.MARK.CIRCLE);
  } else ERROR = play.error;

  return play.success;
}

function sgfSetup(node, name, values) {
  var setupMap = {'AB': C.BLACK, 'AW': C.WHITE, 'AE': C.CLEAR};

  node.setType(explodeSGFList(values), setupMap[name]);
  return true;
}

function sgfMarker(node, name, values) {
  var markerMap = {
    'TW': C.MARK.WHITE_TERRITORY,
    'TB': C.MARK.BLACK_TERRITORY,
    'CR': C.MARK.CIRCLE,
    'TR': C.MARK.TRIANGLE,
    'MA': C.MARK.CROSS,
    'SQ': C.MARK.SQUARE
  };

  node.setMark(explodeSGFList(values), markerMap[name]);
  return true;
}

function sgfComment(node, name, values) {
  node.info.comment = values[0];
  return true;
}

function sgfHandicap(node, name, values) {
  node.info.handicap = values[0];
  return true;
}

function sgfLabel(node, name, values) {
  for(var i=0; i<values.length; i++) {
    var v = values[i], tuple = v.split(':');

    node.setMark(new Coordinate(tuple[0]), tuple[1]);
  }
  return true;
}

function sgfInfo(node, name, values) {
  var field = fieldMap[name];

  node.info[field] = values[0];
  return true;
}

var SGFProperties = {
  'B': sgfMove,
  'W': sgfMove,
  'AB': sgfSetup,
  'AW': sgfSetup,
  'AE': sgfSetup,
  'C': sgfComment,
  'LB': sgfLabel,
  'HA': sgfHandicap,
  'TW': sgfMarker,
  'TB': sgfMarker,
  'CR': sgfMarker,
  'TR': sgfMarker,
  'MA': sgfMarker,
  'SQ': sgfMarker,
  'AN': sgfInfo,
  'CP': sgfInfo,
  'DT': sgfInfo,
  'EV': sgfInfo,
  'GN': sgfInfo,
  'OT': sgfInfo,
  'RO': sgfInfo,
  'RE': sgfInfo,
  'RU': sgfInfo,
  'SO': sgfInfo,
  'TM': sgfInfo,
  'PC': sgfInfo,
  'PB': sgfInfo,
  'PW': sgfInfo,
  'BR': sgfInfo,
  'WR': sgfInfo,
  'BT': sgfInfo,
  'WT': sgfInfo
};

/*
 * Parse SGF string into object tree representation:
 *
 * tree = { sequence: [ <node(s)> ], leaves: [ <subtree(s), if any> ] }
 *
 * Each node is an object containing property identifiers and associated values in array:
 *
 * node = {'B': ['nn'], 'C': ['This is a comment']}
 *
 * @param {String} sgf The SGF in string format, whitespace allowed.
 * @returns {Object} Root node or false on error. Error stored to ERROR variable.
 */
function parseSGF(sgf) {
  var tokens, i, len, token, // for loop vars
      lastBackslash = false, // flag to note if last string ended in escape
      bracketOpen = -1, // the index where bracket opened
      processed = [];

  if('a~b'.split(/(~)/).length === 3) {
    tokens = sgf.split(/([\[\]\(\);])/); // split into an array at '[', ']', '(', ')', and ';', and include separators in array
  } else { // Thank you IE for not working
    var blockStart = 0, delimiters = '[]();';

    tokens = [];

    for(i=0, len=sgf.length; i<len; ++i) {
      if(delimiters.indexOf(sgf.charAt(i)) !== -1) {
        if(blockStart < i)
          tokens.push(sgf.substring(blockStart, i));
        tokens.push(sgf.charAt(i));
        blockStart = i+1;
      }
    }

    if(blockStart < i) // leftovers
      tokens.push(sgf.substr(blockStart, i));
  }

  // process through tokens and push everything into processed, but merge stuff between square brackets into one element, unescaping escaped brackets
  // i.e. ['(', ';', 'C', '[', 'this is a comment containing brackets ', '[', '\\', ']', ']'] becomes:
  // ['(', ';', 'C', '[', 'this is a comment containing brackets []]']
  // after this transformation, it's just '(', ')', ';', 'ID', and '[bracket stuff]' elements in the processed array
  for(i=0, len=tokens.length; i<len; ++i) {
    token = tokens[i];

    if(bracketOpen == -1) { // handling elements outside property values (i.e. square brackets)
      token = token.replace(/^\s+|\s+$/g, ''); // trim whitespace, it is irrelevant here
      if(token == '[') // found one
        bracketOpen = i;
      else if(token !== '') // we are outside brackets, so just push everything nonempty as it is into 'processed'
        processed.push(token);
    } else { // bracket is open, we're now looking for a ] without preceding \
      if(token != ']') { // a text segment
        lastBackslash = (token.charAt(token.length-1) == '\\'); // true if string ends in \
      } else { // a closing bracket
        if(lastBackslash) { // it's escaped - we continue
          lastBackslash = false;
        } else { // it's not escaped - we close the segment
          processed.push(tokens.slice(bracketOpen, i+1).join('').replace(/\\\]/g, ']')); // push the whole thing including brackets, and unescape the inside closing brackets
          bracketOpen = -1;
        }
      }
    }
  }

  // basic error checking
  if(processed.length === 0) {
    ERROR = 'SGF was empty!';
    return false;
  } else if(processed[0] != '(' || processed[1] != ';' || processed[processed.length-1] != ')') {
    ERROR = 'SGF did not start with \'(;\' or end with \')\'!';
    return false;
  }

  // collect 'XY', '[AB]', '[CD]' sequences (properties) in a node into {'XY': ['AB', 'CD']} type of associative array
  // effectively parsing '(;GM[1]FF[4];B[pd])' into ['(', {'GM': ['1'], 'FF': ['4']}, {'B': ['pd']}, ')']

  // start again with 'tokens' and process into 'processed'
  tokens = processed;
  processed = [];

  var node, propertyId = ''; // node under construction, and current property identifier

  // the following code is not strict on format, so let's hope it's well formed
  for(i=0, len=tokens.length; i<len; ++i) {
    token = tokens[i];

    if(token == '(' || token == ')') {
      if(node) { // flush and reset node if necessary
        if(propertyId !== '' && node[propertyId].length === 0) { // last property was missing value
          ERROR = 'Missing property value at ' + token + '!';
          return false;
        }
        processed.push(node);
        node = undefined;
      }

      processed.push(token); // push this token also
    } else if(token == ';') { // new node
      if(node) { // flush if necessary
        if(propertyId !== '' && node[propertyId].length === 0) { // last property was missing value
          ERROR = 'Missing property value at ' + token + '!';
          return false;
        }
        processed.push(node);
      }

      node = {};
      propertyId = ''; // initialize the new node
    } else { // it's either a property identifier or a property value
      if(token.indexOf('[') !== 0) { // it's property identifier
        if(propertyId !== '' && node[propertyId].length === 0) { // last property was missing value
          ERROR = 'Missing property value at ' + token + '!';
          return false;
        }

        if(token in node) { // duplicate key
          ERROR = 'Duplicate property identifier ' + token + '!';
          return false;
        }

        propertyId = token;
        node[propertyId] = []; // initialize new property with empty value array
      } else { // it's property value
        if(propertyId === '') { // we're missing the identifier
          ERROR = 'Missing property identifier at ' + token + '!';
          return false;
        }

        node[propertyId].push(token.substring(1, token.length-1)); // remove enclosing brackets
      }
    }
  }

  tokens = processed;

  // finally, construct a game tree from '(', ')', and sequence arrays - each leaf is {sequence: [ <list of nodes> ], leaves: [ <list of leaves> ]}
  var stack = [], currentRoot = {sequence: [], leaves: []}, lastRoot; // we know first element already: '('

  for(i=1, len=tokens.length; i<len-1; ++i) {
    token = tokens[i];

    if(token == '(') { // enter a subleaf
      if(currentRoot.sequence.length === 0) { // consecutive parenthesis without node sequence in between will throw an error
        ERROR = 'SGF contains a game tree without a sequence!';
        return false;
      }
      stack.push(currentRoot); // save current leaf for when we return
      currentRoot = {sequence: [], leaves: []};
    } else if(token == ')') { // return from subleaf
      if(currentRoot.sequence.length === 0) { // consecutive parenthesis without node sequence in between will throw an error
        ERROR = 'SGF contains a game tree without a sequence!';
        return false;
      }
      lastRoot = currentRoot;
      currentRoot = stack.pop();
      currentRoot.leaves.push(lastRoot);
    } else { // if every '(' is not followed by exactly one array of nodes (as it should), this code fails
      currentRoot.sequence.push(token);
    }
  }

  if(stack.length > 0) {
    ERROR = 'Invalid number of parentheses in the SGF!';
    return false;
  }

  return currentRoot;
}

/*
 * Apply SGF nodes recursively to create a game tree.
 * @returns true on success, false on error. Error message in ERROR.
 */
function recurseRecord(jrecord, gameTree, moveMarks) {
  for(var i=0; i<gameTree.sequence.length; i++) {
    var node = gameTree.sequence[i],
      jnode = jrecord.createNode(true); // clear parent marks

    for(var key in node) {
      if(node.hasOwnProperty(key)) {
        if(!(key in SGFProperties))
          continue;

        if(!SGFProperties[key](jnode, key, node[key], moveMarks)) {
          ERROR = 'Error while parsing node ' + key + ': ' + ERROR;
          return false;
        }
      }
    }
  }

  for(i=0; i<gameTree.leaves.length; i++) {
    var subTree = gameTree.leaves[i], snapshot;

    snapshot = jrecord.createSnapshot();

    if(!recurseRecord(jrecord, subTree, moveMarks))
      return false; // fall through on errors

    jrecord.restoreSnapshot(snapshot);
  }

  return true;
}

/*
 * Convert game tree to a record.
 * @returns {Object} Record or false on failure. Error stored in ERROR.
 */
function gameTreeToRecord(gameTree, moveMarks) {
  var jrecord, root = gameTree.sequence[0], width = 19, height = 19;

  if('SZ' in root) {
    var size = root.SZ[0];

    if(size.indexOf(':') != -1) {
      width = parseInt(size.substring(0, size.indexOf(':')));
      height = parseInt(size.substr(size.indexOf(':')+1));
    } else width = height = parseInt(size);
  }

  jrecord = new Record(width, height);

  if(!recurseRecord(jrecord, gameTree, moveMarks))
    return false;

  jrecord.first(); // rewind to start

  return jrecord;
}

/**
 * Parse SGF and return {@link Record} object(s).
 *
 * @param {String} sgf The SGF file as a string.
 * @param {bool} moveMarks Create move and ko marks in the record.
 * @returns {Object} Record object, array of them, or string on error.
 */
exports.load = function(sgf, moveMarks) {
  var gameTree = parseSGF(sgf);

  if(gameTree === false)
    return ERROR;

  if(gameTree.sequence.length === 0) { // potentially multiple records
    var ret = [];

    if(gameTree.leaves.length === 0)
      return 'Empty game tree!';

    for(var i=0; i<gameTree.leaves.length; i++) {
      var rec = gameTreeToRecord(gameTree, moveMarks);

      if(!rec)
        return ERROR;

      ret.push(rec); // return each leaf as separate record
    }

    return ret;
  }

  return gameTreeToRecord(gameTree, moveMarks);
};

},{"./constants":4,"./coordinate":5,"./record":9}],12:[function(require,module,exports){
'use strict';

var C = require('./constants');

/**
 * Create a jGoBoard stones object. This is a facility that can draw
 * stones and markers on a HTML5 canvas. Only used internally by the
 * library.
 *
 * @param {Object} options Options array.
 * @constructor
 */
var Stones = function(options, images) {
  this.stoneR = options.stone.radius;
  this.gridX = options.grid.x;
  this.gridY = options.grid.x;
  this.markX = this.stoneR * 1.1;
  this.markY = this.stoneR * 1.1;
  this.circleR = this.stoneR * 0.5;
  this.triangleR = this.stoneR * 0.9;
  this.images = images;
};

Stones.prototype.drawStone = function(ctx, type, ox, oy, scale) {
  if(!scale) scale = 1;
  var stone = (type == C.BLACK || type == C.DIM_BLACK) ? this.images.black : this.images.white;

  if(!stone) { // BW
    ctx.fillStyle = (type == C.WHITE) ? '#FFFFFF' : '#000000';
    ctx.beginPath();
    ctx.arc(ox, oy, this.stoneR*scale, 2*Math.PI, false);
    ctx.fill();

    if(type == C.WHITE) {
      ctx.strokeStyle = '#000000';
      ctx.stroke();
    }
  } else {
    // round x, y for crisp rendering
    ctx.drawImage(stone, 0, 0, stone.width, stone.height,
        Math.round(ox - stone.width / 2 * scale),
        Math.round(oy - stone.height / 2 * scale),
        stone.width * scale, stone.height * scale);
  }
};

Stones.prototype.drawShadow = function(ctx, ox, oy, scale) {
  var shadow = this.images.shadow;
  if(!shadow) return;
  if(!scale) scale = 1;

  ctx.drawImage(shadow, 0, 0, shadow.width, shadow.height,
      Math.round(ox - shadow.width / 2 * scale),
      Math.round(oy - shadow.height / 2 * scale),
      shadow.width * scale, shadow.height * scale);
};

Stones.prototype.drawMark = function(ctx, mark, ox, oy) {
  switch(mark) {
    case C.MARK.SQUARE:
      ctx.beginPath();
      ctx.rect(ox - this.markX / 2, oy - this.markY / 2, this.markX, this.markY);
      ctx.stroke();
      break;

    case C.MARK.CROSS:
      ctx.beginPath();
      ctx.moveTo(ox - this.markX / 2, oy + this.markY / 2);
      ctx.lineTo(ox + this.markX / 2, oy - this.markY / 2);
      ctx.moveTo(ox - this.markX / 2, oy - this.markY / 2);
      ctx.lineTo(ox + this.markX / 2, oy + this.markY / 2);
      ctx.stroke();
      break;

    case C.MARK.TRIANGLE:
      ctx.beginPath();
      for(var r=0; r<3; r++) {
        ctx.moveTo(ox + this.triangleR * Math.cos(Math.PI * (0.5 + 2*r/3)),
            oy - this.triangleR * Math.sin(Math.PI * (0.5 + 2*r/3)));
        ctx.lineTo(ox + this.triangleR * Math.cos(Math.PI * (0.5 + 2*(r+1)/3)),
            oy - this.triangleR * Math.sin(Math.PI * (0.5 + 2*(r+1)/3)));
      }
      ctx.stroke();
      break;

    case C.MARK.CIRCLE:
      ctx.beginPath();
      ctx.arc(ox, oy, this.circleR, 2*Math.PI, false);
      ctx.stroke();
      break;

    case C.MARK.BLACK_TERRITORY:
      ctx.globalAlpha=1;
      this.drawStone(ctx, C.BLACK, ox, oy, 0.5);
      break;

    case C.MARK.WHITE_TERRITORY:
      ctx.globalAlpha=1;
      this.drawStone(ctx, C.WHITE, ox, oy, 0.5);
      break;

    case C.MARK.SELECTED:
      ctx.globalAlpha=0.5;
      ctx.fillStyle = '#8080FF';
      //ctx.beginPath();
      ctx.fillRect(ox - this.gridX / 2, oy - this.gridY / 2,
          this.gridX, this.gridY);
      break;

    default: // Label
      // For clear intersections, grid is cleared before shadow cast
      ctx.fillText(mark, ox, oy);
      break;
  }
};

module.exports = Stones;

},{"./constants":4}],13:[function(require,module,exports){
'use strict';

/**
 * Utility function module.
 * @module util
 */

var Coordinate = require('./coordinate');

/**
 * Load images and defined by object and invoke callback when completed.
 *
 * @param {Object} sources A dictionary of sources to load.
 * @param {function} callback A callback function to call with image dict.
 */
exports.loadImages = function(sources, callback) {
  var images = {}, imagesLeft = 0;

  for(var src in sources) // count non-false properties as images
    if(sources.hasOwnProperty(src) && sources[src])
      imagesLeft++;

  var countdown = function() {
    if(--imagesLeft <= 0) {
      callback(images);
    }
  };

  for(src in sources) { // load non-false properties to images object
    if(sources.hasOwnProperty(src) && sources[src]) {
      /* global Image */
      images[src] = new Image();
      images[src].onload = countdown;
      images[src].src = sources[src];
    }
  }
};

/**
 * Helper function to create coordinates for standard handicap placement.
 *
 * @param {int} size Board size (9, 13, 19 supported).
 * @param {itn} num Number of handicap stones.
 * @returns {Array} Array of Coordinate objects.
 */
exports.getHandicapCoordinates = function(size, num) {
  // Telephone dial style numbering
  var handicapPlaces = [[], [], [3,7], [3,7,9], [1,3,7,9], [1,3,5,7,9],
      [1,3,4,6,7,9], [1,3,4,5,6,7,9], [1,2,3,4,6,7,8,9],
      [1,2,3,4,5,6,7,8,9]];
  var places = handicapPlaces[num], offset = (size <= 9 ? 2 : 3),
      step = (size - 1) / 2 - offset, coords = [];

  if(places) {
    for(var n=0; n<places.length; n++) {
      var i = (places[n]-1) % 3, j = Math.floor((places[n]-1) / 3);
      coords.push(new Coordinate(offset+i*step, offset+j*step));
    }
  }

  return coords;
};

/**
 * Deep extend an object.
 *
 * @function extend
 * @param {Object} dest Destination object to extend.
 * @param {Object} src Source object which properties will be copied.
 * @returns {Object} Extended destination object.
 */
exports.extend = function(dest, src) {
  for(var key in src) {
    if(src.hasOwnProperty(key)) {
      if(typeof src[key] === 'object') {
        if(!dest[key] || (typeof dest[key] !== 'object'))
          dest[key] = {}; // create/overwrite if necessary
        exports.extend(dest[key], src[key]);
      } else dest[key] = src[key];
    }
  }

  return dest;
};

},{"./coordinate":5}],14:[function(require,module,exports){
'use strict';
var JGO = require('./JGO');
window.JGO = JGO; // expose as global object

},{"./JGO":6}]},{},[14]);
