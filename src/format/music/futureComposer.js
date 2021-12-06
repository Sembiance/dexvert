import {Format} from "../../Format.js";

export class futureComposer extends Format
{
	name         = "Future Composer Module";
	website      = "http://fileformats.archiveteam.org/wiki/Future_Composer_v1.x_module";
	ext          = [".fc", ".fc13", ".fc14", ".smc", ".smod", ".bsi"];
	magic        = ["Future Composer "];	// trailing space on purpose
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
