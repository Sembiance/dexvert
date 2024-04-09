import {Format} from "../../Format.js";

export class promizer extends Format
{
	name         = "Promizer Module";
	ext          = [".pm0", ".pm01", ".pm1", ".pm10", ".pm2", ".pm20", ".pm4", ".pm40", ".pmz"];
	magic        = [/^Promizer .*module$/, "Promizer 1.0c/1.8", "Promizer 2.0"];
	metaProvider = ["muscInfo"];
	converters   = ["uade123"];
}
