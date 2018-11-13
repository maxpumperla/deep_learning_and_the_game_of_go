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
