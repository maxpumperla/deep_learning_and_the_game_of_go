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
