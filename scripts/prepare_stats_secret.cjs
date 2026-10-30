// Generate a Worker stats secret and encrypt its recovery copy for the owner.
// Only the public recovery key is provided to the runner.
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const output = process.env.STATS_SECRET_DIR;
const encodedKey = process.env.STATS_RECOVERY_PUBLIC_KEY;
if (!output || !encodedKey) throw new Error('Missing stats recovery configuration');
const publicKey = crypto.createPublicKey({
  key: Buffer.from(encodedKey, 'base64'),
  format: 'der',
  type: 'spki',
});
if (publicKey.asymmetricKeyType !== 'rsa' || publicKey.asymmetricKeyDetails.modulusLength < 3072) {
  throw new Error('Recovery key must be RSA with at least 3072 bits');
}
const secret = crypto.randomBytes(32).toString('base64url');
const encrypted = crypto.publicEncrypt({
  key: publicKey,
  padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
  oaepHash: 'sha256',
}, Buffer.from(secret));
fs.mkdirSync(output, { mode: 0o700 });
fs.writeFileSync(path.join(output, 'STATS_TOKEN.rsa-oaep'), encrypted, { mode: 0o600, flag: 'wx' });
fs.writeFileSync(path.join(output, 'STATS_TOKEN'), secret, { mode: 0o600, flag: 'wx' });
// Register before any following process can log the generated secret.
process.stdout.write(`::add-mask::${secret}\n`);
console.log('Prepared a random stats secret and encrypted recovery copy.');
