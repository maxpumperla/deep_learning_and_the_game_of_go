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
