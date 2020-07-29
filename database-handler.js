import mongoose from 'mongodb';
import dotenv from 'dotenv';
import Cloudant from '@cloudant/cloudant';
dotenv.config();

export async function getTransactionData() {
    var cloudant = new Cloudant({
        url: process.env.CLOUDANT_URL, plugins: {
            iamauth: {
                iamApiKey: process.env.CLOUDANT_APIKEY
            }
        }
    });

    var user_transactions_db = cloudant.db.use('user-transactions');
    var rounded_up_db = cloudant.db.use('round-up');
    var donations_db = cloudant.db.use('donations');

    var user_transactions_docs = [];
    var rounded_up_docs = rounded_up_db.list({ include_docs: true });
    var donations_docs = donations_db.list({ include_docs: true });

    // Read all DB documents
    var transactions = function () {
        user_transactions_db.list({ include_docs: true }, function (err, data) {
            data.rows.forEach(doc => {
                user_transactions_docs.push(doc.doc);
            });
            console.log(user_transactions_docs);
        });
    };
    transactions();
    await new Promise(r => setTimeout(r, 5000));
    return user_transactions_docs;
}


// ALL OLD MONGODB CODE
const MongoClient = mongoose.MongoClient;
const url = `mongodb+srv://dbUser:${process.env.DB_PASS}@cluster0.u5bz6.mongodb.net/userdb?retryWrites=true&w=majority`;

let _db;

export function connectToServer(callback) {
    MongoClient.connect(url, { useUnifiedTopology: true, useNewUrlParser: true, }, (err, client) => {
        if (err) console.log('MongoDb Error: ', err);
        _db = client.db('userdb');
        return callback(err);
    })
}

export async function createUserAccount(profile) {
    const data = {
        id: profile.id,
        name: profile.displayName,
        balance: 0,
        roundedBalance: 0,
        access_token: null,
        item_id: null
    };

    _db.collection('userdb').insertOne(data);
    return await data;
}

export async function getUserAccount(profile) {
    const query = {
        id: profile.id
    };

    let account = await _db.collection('userdb').find(query).toArray();
    return await account[0];
}

export async function getUserAccountByID(user_id) {
    const query = {
        id: user_id
    }

    let account = await _db.collection('userdb').find(query).toArray();
    return await account[0];
}

export async function updateUserLinkTokens(user_id, access_token, item_id) {
    const query = {
        id: user_id
    }
    const updatedValues = {
        $set: { access_token: access_token, item_id: item_id }
    }
    await _db.collection('userdb').updateOne(query, updatedValues, (err, res) => {
        if (err) throw err;
    })
}
// ALL OLD MONGODB CODE
