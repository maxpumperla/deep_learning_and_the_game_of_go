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
