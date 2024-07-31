import {Format} from "../../Format.js";

export class hyperArchive extends Format
{
	name       = "Hyper Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Hyper_archive";
	ext        = [".hyp"];
	magic      = ["Hyper archive", /^Hyper [\d.]+ Archiv gefunden/, /^HYP archive data/];
	converters = ["hyper"];
}
