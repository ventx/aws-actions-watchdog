const https = require("https"),
  vm = require("vm"),
  AWS = require("aws-sdk");

let url = "https://awsiamconsole.s3.amazonaws.com/iam/assets/js/bundles/policies.js";
let bucketName = "{{S3BucketName}}"
let snsTopicArn = "{{SnsTopicArn}}"

exports.handler = async event => {
  return main()
};

function main() {
    return new Promise(function(resolve, reject) {
    let s3 = new AWS.S3();
    let sns = new AWS.SNS();

    https.get(url, res => {
        let data = "";
        res.on("data", chunk => {
          data += chunk;
        });
        res.on("end", () => {
          let actions = getActions(data)
          let getParams = {
            Bucket: bucketName,
            Key: "services.json"
          };

          s3.getObject(getParams, function(err, data) {
            if (err) {
              if (err.code == "NoSuchKey") {
                saveValues(s3, actions, reject, resolve);
              } else {
                reject(err);
              }
            } else {
              var oldActions = JSON.parse(data.Body.toString('utf-8'));
              var newActions = actions.filter(x => !oldActions.includes(x));
              writeToSnsTopic(sns,'New Actions', JSON.stringify(newActions, null, 2))
              console.log(newActions);
              saveValues(s3, actions, reject, resolve);
            }
          });
        });
      })
      .on("error", e => {
        reject(Error(e));
      });
  });
}


function writeToSnsTopic(sns, title, message) {
  var params  ={ 
    Message: message,
    Subject: title,
    TopicArn: snsTopicArn
  }

  return sns.publish(params).promise()
}

function getActions(data) {
  let defineTypes = "let app = {};";
  defineTypes += "let EnvInfo = {};";
  defineTypes +=
    "let _ = { has: function () { return false; }, extend: function () { }};";
  defineTypes += "let window = { EnvInfo: {} };";
  data = defineTypes + data + ";app;";
  let result = vm.runInNewContext(data);
  let listOfListOfActions = Object.values(
    result.PolicyEditorConfig.serviceMap
  ).map(x => x.Actions.map(a => x.StringPrefix + ":" + a));
  return listOfListOfActions.reduce(function(a, b) {
    return a.concat(b);
  });
}

function saveValues(s3, actions, reject, resolve) {
  let params = {
    Bucket: "{{S3BucketName}}",
    Key: "services.json",
    Body: JSON.stringify(actions)
  };
  s3.putObject(params, function(err, data) {
    if (err) {
      reject(err);
    } else {
      resolve(200);
    }
  });
}
