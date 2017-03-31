rs.initiate({
    _id: 'rs',
    members: [
        {_id: 0, priority: 2, host: 'mongo-a:27018'},
        {_id: 1, priority: 1, host: 'mongo-b:27019'},
        {_id: 2, priority: 1, host: 'mongo-c:27020'}
    ]
})