import {Format} from "../../Format.js";

export class pgpPublicKey extends Format
{
	name           = "PGP Public Key";
	website        = "http://fileformats.archiveteam.org/wiki/PGP_public_key";
	ext            = [".asc", ".aexpk", ".pgp", ".pub"];
	forbidExtMatch = true;
	magic          = ["PGP public key block", "PGP armored data, public key block"];
	untouched      = true;
	metaProvider   = ["text"];
}
