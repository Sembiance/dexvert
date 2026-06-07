import {Format} from "../../Format.js";

export class motorheadPDI extends Format
{
	name           = "Motorhead PDI game archive";
	ext            = [".pdi"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PDI_PDI1( |$)/];
	converters     = ["gameextractor[codes:PDI_PDI1]"];
}
