import {Format} from "../../Format.js";

export class novoTrade extends Format
{
	name         = "NovoTrade Packer";
	website      = "http://fileformats.archiveteam.org/wiki/NovoTrade_Packer";
	ext          = [".ntp"];
	magic        = ["NovoTrade Packer module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
}
