import {assertStrictEquals} from "https://deno.land/std@0.111.0/testing/asserts.ts";
import {DexFile} from "../../src/DexFile.js";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import {fileUtil} from "xutil";
import {encode as base64Encode} from "https://deno.land/std@0.113.0/encoding/base64.ts";

Deno.test("create", async () =>
{
	// cwd file
	let a = await DexFile.create(path.relative(Deno.cwd(), "/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt"));
	assertStrictEquals(a.root, Deno.cwd());
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
	assertStrictEquals(a.base, "some.big.txt.file.txt");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.name, "some.big.txt.file");
	assertStrictEquals(a.ext, ".txt");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 6);
	assertStrictEquals(a.ts, 1_635_685_469_027);
	assertStrictEquals(a.preExt, ".some");
	assertStrictEquals(a.preName, "big.txt.file.txt");

	// absolute path, root and clonse
	a = await DexFile.create("/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
	const b = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", rel : "some.big.txt.file.txt"});
	const c = b.clone();
	const d = b.clone();
	d.changeRoot("/some/random/dir", {keepRel : true});
	[a, b, c].forEach(o =>
	{
		assertStrictEquals(o.rel, "some.big.txt.file.txt");
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.absolute, "/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
		assertStrictEquals(o.base, "some.big.txt.file.txt");
		assertStrictEquals(o.dir, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.name, "some.big.txt.file");
		assertStrictEquals(o.ext, ".txt");
		assertStrictEquals(o.isFile, true);
		assertStrictEquals(o.isDirectory, false);
		assertStrictEquals(o.isSymlink, false);
		assertStrictEquals(o.size, 6);
		assertStrictEquals(o.ts, 1_635_685_469_027);
		assertStrictEquals(o.preExt, ".some");
		assertStrictEquals(o.preName, "big.txt.file.txt");
	});

	// subDir file
	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", rel : "subDir/txt.b"});
	assertStrictEquals(a.rel, "subDir/txt.b");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b");
	assertStrictEquals(a.base, "txt.b");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "txt");
	assertStrictEquals(a.ext, ".b");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 8);
	assertStrictEquals(a.ts, 1_635_685_484_995);
	assertStrictEquals(a.preExt, ".txt");
	assertStrictEquals(a.preName, "b");

	// symlink
	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", rel : "subDir/symlinkFile"});
	assertStrictEquals(a.rel, "subDir/symlinkFile");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile");
	assertStrictEquals(a.base, "symlinkFile");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "symlinkFile");
	assertStrictEquals(a.ext, "");
	assertStrictEquals(a.isFile, false);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, true);
	assertStrictEquals(a.ts, 1_635_685_795_866);
	assertStrictEquals(a.preExt, "");
	assertStrictEquals(a.preName, "symlinkFile");

	// directory
	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", rel : "subDir/more_sub/third"});
	assertStrictEquals(a.rel, "subDir/more_sub/third");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third");
	assertStrictEquals(a.base, "third");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub");
	assertStrictEquals(a.name, "third");
	assertStrictEquals(a.ext, "");
	assertStrictEquals(a.isFile, false);
	assertStrictEquals(a.isDirectory, true);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.ts, 1_635_685_489_475);
	assertStrictEquals(a.preExt, "");
	assertStrictEquals(a.preName, "third");

	// absolute path with root
	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files", absolute : "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"});
	assertStrictEquals(a.rel, "subDir/txt.b");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b");
	assertStrictEquals(a.base, "txt.b");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "txt");
	assertStrictEquals(a.ext, ".b");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 8);
	assertStrictEquals(a.ts, 1_635_685_484_995);
	assertStrictEquals(a.preExt, ".txt");
	assertStrictEquals(a.preName, "b");
});

Deno.test("changeRoot", async () =>
{
	let a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", rel : "subDir/txt.b"});
	const b = a.clone();
	b.changeRoot("/tmp/dir/whatever/", {keepRel : true});

	// check that original was not changed
	assertStrictEquals(a.rel, "subDir/txt.b");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b");
	assertStrictEquals(a.base, "txt.b");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "txt");
	assertStrictEquals(a.ext, ".b");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 8);
	assertStrictEquals(a.ts, 1_635_685_484_995);
	assertStrictEquals(a.preExt, ".txt");
	assertStrictEquals(a.preName, "b");

	// check that clone was changed
	assertStrictEquals(b.rel, "subDir/txt.b");
	assertStrictEquals(b.root, "/tmp/dir/whatever");
	assertStrictEquals(b.absolute, "/tmp/dir/whatever/subDir/txt.b");
	assertStrictEquals(b.base, "txt.b");
	assertStrictEquals(b.dir, "/tmp/dir/whatever/subDir");
	assertStrictEquals(b.name, "txt");
	assertStrictEquals(b.ext, ".b");
	assertStrictEquals(b.isFile, true);
	assertStrictEquals(b.isDirectory, false);
	assertStrictEquals(b.isSymlink, false);
	assertStrictEquals(b.size, 8);
	assertStrictEquals(b.ts, 1_635_685_484_995);
	assertStrictEquals(b.preExt, ".txt");
	assertStrictEquals(b.preName, "b");

	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files", rel : "subDir/txt.b"});
	a.changeRoot("/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.rel, "txt.b");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b");
	assertStrictEquals(a.base, "txt.b");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "txt");
	assertStrictEquals(a.ext, ".b");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 8);
	assertStrictEquals(a.ts, 1_635_685_484_995);
	assertStrictEquals(a.preExt, ".txt");
	assertStrictEquals(a.preName, "b");

	a.changeRoot("/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub");
	assertStrictEquals(a.rel, "../txt.b");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b");
	assertStrictEquals(a.base, "txt.b");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "txt");
	assertStrictEquals(a.ext, ".b");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 8);
	assertStrictEquals(a.ts, 1_635_685_484_995);
	assertStrictEquals(a.preExt, ".txt");
	assertStrictEquals(a.preName, "b");
});

Deno.test("rename", async () =>
{
	const tmpPath = await fileUtil.genTempPath(undefined, ".txt");
	const tmpDir = path.dirname(tmpPath);
	const tmpFilename = path.basename(tmpPath);
	await Deno.copyFile("/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt", tmpPath);

	const a = await DexFile.create(tmpPath);
	assertStrictEquals(a.root, tmpDir);
	assertStrictEquals(a.absolute, path.join(tmpDir, tmpFilename));
	assertStrictEquals(a.base, tmpFilename);
	assertStrictEquals(a.dir, tmpDir);
	assertStrictEquals(a.name, path.basename(tmpFilename, ".txt"));
	assertStrictEquals(a.ext, ".txt");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 6);
	assertStrictEquals(a.preName, "txt");

	await a.rename("somethingElse.png");
	assertStrictEquals(a.root, tmpDir);
	assertStrictEquals(a.absolute, path.join(tmpDir, "somethingElse.png"));
	assertStrictEquals(a.base, "somethingElse.png");
	assertStrictEquals(a.dir, tmpDir);
	assertStrictEquals(a.name, "somethingElse");
	assertStrictEquals(a.ext, ".png");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 6);
	assertStrictEquals(a.preExt, ".somethingElse");
	assertStrictEquals(a.preName, "png");

	await a.rename(tmpFilename);

	await fileUtil.unlink(tmpPath);
});

Deno.test("pretty", async () =>
{
	const a = await DexFile.create("/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
	assertStrictEquals(base64Encode(a.pretty()), "G1szODs1OzI1MG1GG1swbSAbWzk3bSAgICA2YhtbMG0gG1s5NW0vbW50L2NvbXBlbmRpdW0vRGV2TGFiL2RleHZlcnQvdGVzdC9maWxlcxtbMG0bWzk2bS8bWzBtG1s5NW1zb21lLmJpZy50eHQuZmlsZS50eHQbWzBt");
});

Deno.test("serialize", async () =>
{
	const a = await DexFile.create("/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
	assertStrictEquals(JSON.stringify(a.serialize()), `{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"some.big.txt.file.txt","absolute":"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt","transformed":false,"base":"some.big.txt.file.txt","dir":"/mnt/compendium/DevLab/dexvert/test/files","name":"some.big.txt.file","ext":".txt","preExt":".some","preName":"big.txt.file.txt","isFile":true,"isDirectory":false,"isSymlink":false,"size":6,"ts":1635685469027}`);	// eslint-disable-line max-len
});

Deno.test("deserialize", () =>
{
	const a = DexFile.deserialize(JSON.parse(`{"root":"/mnt/compendium/DevLab/dexvert/test/files","rel":"some.big.txt.file.txt","absolute":"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt","transformed":false,"base":"some.big.txt.file.txt","dir":"/mnt/compendium/DevLab/dexvert/test/files","name":"some.big.txt.file","ext":".txt","preExt":".some","preName":"big.txt.file.txt","isFile":true,"isDirectory":false,"isSymlink":false,"size":6,"ts":1635685469027}`));	// eslint-disable-line max-len, no-restricted-syntax
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
	assertStrictEquals(a.base, "some.big.txt.file.txt");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.name, "some.big.txt.file");
	assertStrictEquals(a.ext, ".txt");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 6);
	assertStrictEquals(a.ts, 1_635_685_469_027);
	assertStrictEquals(a.preExt, ".some");
	assertStrictEquals(a.preName, "big.txt.file.txt");
});
