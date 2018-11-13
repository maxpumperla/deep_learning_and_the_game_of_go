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
