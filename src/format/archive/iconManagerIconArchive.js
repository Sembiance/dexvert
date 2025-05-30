import {Format} from "../../Format.js";

export class iconManagerIconArchive extends Format
{
	name       = "Icon Manager Icon Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Icon_Manager_icon_archive";
	ext        = [".ica"];
	magic      = ["Icon Manager Icon Archive", "deark: iconmgr_ica"];
	converters = ["deark[module:iconmgr_ica]"];
}
