import {Format} from "../../Format.js";

export class dynamicPublisherStamp extends Format
{
	name       = "Dynamic Publisher Stamp";
	website    = "http://fileformats.archiveteam.org/wiki/Dynamic_Publisher";
	ext        = [".stp"];
	magic      = ["Dynamic Publisher Stamp"];
	weakMagic  = true;
	converters = ["recoil2png"];
	verify     = ({meta}) => meta.height>3 && meta.width>3 && meta.width<2000 && meta.height<2000;
}
