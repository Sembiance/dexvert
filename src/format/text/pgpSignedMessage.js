import {Format} from "../../Format.js";

export class pgpSignedMessage extends Format
{
	name         = "PGP Signed Message";
	website      = "http://fileformats.archiveteam.org/wiki/PGP";
	magic        = ["PGP signed message", "PGP clear text signed message"];
	untouched    = true;
	metaProvider = ["text"];
}
