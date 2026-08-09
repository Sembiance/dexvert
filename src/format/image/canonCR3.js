import {Format} from "../../Format.js";

export class canonCR3 extends Format
{
	name         = "Canon CR3";
	ext          = [".cr3"];
	magic        = ["Canon Digital Camera RAW image", /^fmt\/1595( |$)/];
	metaProvider = ["darkTable"];
	converters   = ["darktable_cli", "gimp[matchType:magic]"];
}
