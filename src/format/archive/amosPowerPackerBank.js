import {Format} from "../../Format.js";

export class amosPowerPackerBank extends Format
{
	name       = "AMOS Power Packer Bank";
	ext        = [".abk"];
	weakExt    = [".abk"];
	magic      = ["AMOS PowerPacker bank"];

	// xfdDecrunch leaves an amos bank file without a bank header, the addHeader will add it back in so can properly identify the output files
	converters = ["xfdDecrunch[addHeader]"];
}
