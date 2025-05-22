import Axis


def broadcastUpdate(wsmanager, axes: list[Axis]):
    # Broadcast an update on all positions of all motors
    pos = bulkRequest(axes, "pos")
    ont = bulkRequest(axes, "ontarget")

    wsmanager.broadcast({"position": pos, "ontarget": ont})




def bulkRequest(axes: list[Axis], request: str) -> dict:
    """
    Bulk request a parameter from the given axis
    @param axes: list of axes to request
    @param request: Request to send: pos, ontarget
    @return: dict[axis, response]
    """
    responses = {}  # dict where we store the responses, format [axis, response]

    # First we retrieve the PI controllers from the axes list. We will then brute force it, i.e. query every
    # controller we find, and put every single axis we find into the dict, regardless of if it's in the axes list.
    # These two big loops below are only for PI controllers

    PIcontrollers = []  # List of PI controllers we have found
    toRemove = []  # Axes we are done with and want to remove, so we don't remove during the loop (funny things happen)
    for axis in axes:
        if axis is type(Axis.PIAxis):
            #  We have come across a PI axis, lets see if we already have it in the list
            if axis.controller not in PIcontrollers:
                # Add it to the list
                PIcontrollers.append(axis.controller)
            # Otherwise we do nothing, the controller is already in the list
            # We can now remove the axis from the list
            toRemove.append(axis)

    # Remove the processed axes
    axes = [x for x in axes if x not in toRemove]

    # We have the controllers, lets get the responses from them
    for controller in PIcontrollers:
        # Query the correct request
        res = {}
        match request:
            case 'pos':
                res = controller.getPos()
            case 'ontarget':
                res = controller.onTarget()
            case _:
                # Invalid request
                raise Exception("Bulk request is invalid: " + request + ". Valid ones: pos, ontarget")
        # We have the response from the controller, lets add to existing responses
        responses = responses | res


    # We have bulk requested PI axes, now let's do Standa and Dummies, which don't group axes into controllers
    # For now, we do the naive approach, without parallelization
    toRemove = []  # Axes we are done with and want to remove, so we don't remove during the loop (funny things happen)
    for axis in axes:
        # Just assume the rest is either standa or dummies, if you add other brands which work differently
        # you will need to differentiate between them, right now this works good enough.
        if True:
            # Query the correct request
            match request:
                case 'pos':
                    res = axis.getPos()
                case 'ontarget':
                    res = axis.onTarget()
                case _:
                    # Invalid request
                    raise Exception("Bulk request is invalid: " + request + ". Valid ones: pos, ontarget")

            # Grab the axis name and put the result in the dict
            responses[axis.axis] = res
            # Remove axis from the axes list
            toRemove.append(axis)

    # Remove the processed axes
    axes = [x for x in axes if x not in toRemove]

    #  Axes list should be empty, check if we have any left over
    if len(axes) > 0:
        raise Exception("Not all axes have been processed: " + str(axes))

    # All done, return the responses
    return responses




