/*
import {Format} from "../../Format.js";

export class derCertificate extends Format
{
	name = "DER Encoded Certificate";
	ext = [".cer"];
	forbidExtMatch = true;
	magic = ["DER encoded X509 Certificate","Certificate, Version=3"];

steps = [null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "DER Encoded Certificate",
	ext            : [".cer"],
	forbidExtMatch : true,
	magic          : ["DER encoded X509 Certificate", "Certificate, Version=3"]
};

exports.steps = [() => ({program : "openssl", flags : {sslCommand : "x509", encodingType : "der"}})];

*/