import {Format} from "../../Format.js";

export class sqlLite3 extends Format
{
	name       = "SQLLite3 Database";
	website    = "http://fileformats.archiveteam.org/wiki/SQLite";
	ext        = [".sqlite", ".sqlite3", ".db"];
	magic      = [
		// generic
		"SQLite 3.x database", "Format: SQLite 3 database", "application/vnd.sqlite3", /^fmt\/729( |$)/,

		// app specific
		"Kexi database"
	];
	converters = ["unSqlite3"];
}
