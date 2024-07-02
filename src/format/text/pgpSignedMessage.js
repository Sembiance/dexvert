import {Format} from "../../Format.js";

export class pgpSignedMessage extends Format
{
	name         = "PGP Message";
	website      = "http://fileformats.archiveteam.org/wiki/PGP";
	magic        = ["PGP signed message", "PGP clear text signed message", "PGP ASCII-Armor", "PGP message, ASCII text", "PGP Nachricht", /^PGP message$/, /^PGP armored data, (signed )?message/];
	untouched    = true;
	metaProvider = ["text"];
}
