
const https = require('https'),
    vm = require('vm'),
    AWS = require('aws-sdk');

let url = "https://awsiamconsole.s3.amazonaws.com/iam/assets/js/bundles/policies.js"

exports.handler = async function(event) {
  const promise = new Promise(function(resolve, reject) {
    let s3 = new AWS.S3();
    s3.putObject()
    https.get(url, (res) => {
        let data = ""
        res.on('data', (chunk) => {
            data += chunk
        })
        res.on('end', () => {
          let defineTypes = 'let app = {};'  
          defineTypes += 'let EnvInfo = {};'
          defineTypes += 'let _ = { has: function () { return false; }, extend: function () { }};'
          defineTypes += 'let window = { EnvInfo: {} };'
          data = defineTypes + data + ";app;"
          let result = vm.runInThisContext(data, url)
          let json = JSON.stringify(result)
          params = {Bucket: "{{S3BucketName}}", Key: "services.json", Body: json  }
          s3.putObject(params, function(err,data) {
            if(err) {
              reject(err)
            } else {
              resolve(res.statusCode)
            }
          })
        })
      }).on('error', (e) => {
        reject(Error(e))
      })
    })
  return promise
}