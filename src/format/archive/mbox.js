import {Format} from "../../Format.js";

export class mbox extends Format
{
	name       = "Mailbox";
	website    = "http://fileformats.archiveteam.org/wiki/Mbox";
	ext        = [".mbox"];
	magic      = ["Standard Unix Mailbox"];
	converters = ["unmbox"];
}
