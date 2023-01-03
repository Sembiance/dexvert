import {Format} from "../../Format.js";

export class sqlLite3 extends Format
{
	name       = "SQLLite3 Database";
	website    = "http://fileformats.archiveteam.org/wiki/SQLite";
	ext        = [".sqlite", ".sqlite3", ".db"];
	magic      = ["SQLite 3.x database", /^fmt\/729( |$)/];
	converters = ["unSqlite3"];
}
