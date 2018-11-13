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
