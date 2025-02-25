'use strict'

$(document).ready(function(){
    $("#allCompanies").DataTable({
        pageLength: 15,
        lengthMenu: [15, 30, 45, 60, 75, 90, 105, 120],
        "columnDefs": [{
            "searchable": false,
            "orderable": false,
            "targets": [6]
        }],
        order: [[1, 'asc']],
        responsive: true,
    });
    $('#allCompanies').on('click', '.change-company-group', function(){
        var cid = $(this).attr('data-id');

        $('#company').val();
        $('#company').val(cid);
    });
    $('#allCompanies').on('click', '.delete-company', function(){
        var cid = $(this).attr('data-id');

        $('#dcid').val();
        $('#dcid').val(cid);
    });
    $('#allCompanyEmails').on('click', '.delete-company-email', function(){
        var eid = $(this).attr('data-id');

        $('#deid').val();
        $('#deid').val(eid);
    });

    $('#allCompanyUsers').on('click', '.delete-company-user', function(){
        var uid = $(this).attr('data-id');

        $('#duid').val();
        $('#duid').val(uid);
    });
    
    $('#allCompanyLeads').on('click', '.delete-company-lead', function(){
        var clid = $(this).attr('data-id');

        $('#dclid').val();
        $('#dclid').val(clid);
    });

    $('.lead-info .edit').on('click', function(){
        $('.lead-info input.form-control.editable').removeAttr('readonly');
        $('.lead-info select.form-control.editable').removeAttr('disabled');
        $('.lead-info .edit').addClass('d-none');
        $('.lead-info .cancel').removeClass('d-none');
        $('.lead-info .action').removeClass('d-none');
    });
    $('.lead-info .cancel').on('click', function(){
        $('.lead-info input.form-control.editable').attr('readonly', true);
        $('.lead-info select.form-control.editable').attr('disabled', true);
        $('.lead-info .edit').removeClass('d-none');
        $('.lead-info .cancel').addClass('d-none');
        $('.lead-info .action').addClass('d-none');
    });
    
    $('#allLeads').on('click', '.delete-lead', function(){
        var lid = $(this).attr('data-id');

        $('#dlid').val();
        $('#dlid').val(lid);
    });
    $('#allLeads').on('click', '.send-lead', function(){
        var lid = $(this).attr('data-id');

        $('#lid').val();
        $('#lid').val(lid);
    });
    $('#allLeads').on('click', '.sent-leads', function(){
        var lid = $(this).attr('data-id');
        var csrftoken = $("[name=csrfmiddlewaretoken]").val();

        $.ajax({
            url: "/work/fetch-email-transactions-by-lead",
            type: "POST",
            dataType: 'json',
            data: {lid:lid, csrfmiddlewaretoken: csrftoken},
            success: function(response){
                $.each(response.data, function(i, item){
                    var htmlRows = '';
                    htmlRows += '<tr>';
                    htmlRows += '<td>'+item.date+'</td>';
                    htmlRows += '<td>'+item.time+'</td>';
                    htmlRows += '<td>'+item.phone+'</td>';
                    htmlRows += '<td>'+item.email+'</td>';
                    htmlRows += '<td>'+item.status+'</td>';
                    htmlRows += '</tr>';

                    $('.transactions').append(htmlRows);
                });
            },
            error: function(response, errorThrown){
                console.log(errorThrown);
            }, 
        });
    });

    $('#allContacts').on('click', '.delete-contact', function(){
        var cid = $(this).attr('data-id');

        $('#dcid').val();
        $('#dcid').val(cid);
    });
    
    $('.country').on('change', function(){
        var country = $(this).val();

        var csrftoken = $("[name=csrfmiddlewaretoken]").val();

        $.ajax({
            url: "/work/fetch-states-by-country",
            type: "POST",
            dataType: 'json',
            data: {country:country, csrfmiddlewaretoken: csrftoken},
            success: function(response){
                var len = 0;
                if(response.data != null){
                    len = response.data.length;
                }
                if(len > 0){
                    $(".state").empty();
                    var option = "<option value='' hidden> -- Select State -- </option>";
                    $(".state").append(option); 
                    for(var i=0; i<len; i++){
                        var name = response.data[i].name;
                        
                        var option = "<option value='"+name+"'>"+name+"</option>";
                        $(".state").append(option); 
                    }
                }
            },
            error: function(response, errorThrown){
                console.log(errorThrown);
            }, 
        });
    });
    $('.country, .company').select2({ theme: "bootstrap-5", templateResult: bgformat, templateSelection: bgformat })

    $('#allGroups').DataTable({
        pageLength: 15,
        lengthMenu: [15, 30, 45, 60, 75, 90, 105, 120],
        "columnDefs": [{
            "searchable": false,
            "orderable": false,
            "targets": [4]
        }],
        order: [[0, 'desc']],
        responsive: true,
    });
    $('#filter').on('change', function(){
        var filter = $(this).val();

        if(filter === 'Custom'){
            $('.rules').removeClass('d-none');
        }else{
            $('.rules').addClass('d-none');
        }
    });
    $(document).on('click', '#checkAll', function() {
        $(".itemRow").prop("checked", this.checked);
    });
    $(document).on('click', '.itemRow', function() {
        if ($('.itemRow:checked').length == $('.itemRow').length) {
            $('#checkAll').prop('checked', true);
        } else {
            $('#checkAll').prop('checked', false);
        }
    });
    var counting = $(".itemRow").length;
    $(document).on('click', '#addmore', function(){
        counting++;
        var htmlRows = '';
        htmlRows += '<tr>';
        htmlRows += '<td scope="row" data-label="" class="text-center"><input class="itemRow" type="checkbox"></td>';
        htmlRows += '<td scope="row" data-label="Field">';
        htmlRows += '<select class="field form-control custom active" name="field[]" id="field_'+counting+'">';
        htmlRows += '<option value="" hidden> -- Select Field -- </option>';
        htmlRows += '<option value="name">Name</option>';
        htmlRows += '<option value="email">Email</option>';
        htmlRows += '<option value="phone">Phone</option>';
        htmlRows += '<option value="make">Make</option>';
        htmlRows += '<option value="model">Model</option>';
        htmlRows += '<option value="year">Year</option>';
        htmlRows += '<option value="size">Size</option>';
        htmlRows += '<option value="part">Part</option>';
        htmlRows += '<option value="website">Website</option>';
        htmlRows += '</select>';
        htmlRows += '</td>';
        htmlRows += '<td scope="row" data-label="Condition">';
        htmlRows += '<select class="condition form-control custom active" name="condition[]" id="condition_'+counting+'">';
        htmlRows += '<option value="" hidden> -- Select Condition -- </option>';
        htmlRows += '<option value="equal">Equal To</option>';
        htmlRows += '<option value="not_equal">Not Equal To</option>';
        htmlRows += '<option value="greater_than">Greater Than</option>';
        htmlRows += '<option value="greater_than_equal">Greater Than or Equal To</option>';
        htmlRows += '<option value="lesser_than">Lesser Than</option>';
        htmlRows += '<option value="lesser_than_equal">Lesser Than or Equal To</option>';
        htmlRows += '<option value="not_null">Not Null</option>';
        htmlRows += '</select>';
        htmlRows += '</td>';
        htmlRows += '<td scope="row" data-label="Value"><input type="text" class="value form-control custom active" name="value[]" id="value_'+counting+'" placeholder="Enter Value"></td>';
        htmlRows += '<td scope="row" data-label="Logic">';
        htmlRows += '<select class="logic form-control custom active" name="logic[]" id="logic_'+counting+'">';
        htmlRows += '<option value="" hidden> -- Select Logic -- </option>';
        htmlRows += '<option value="none">None</option>';
        htmlRows += '<option value="and">And</option>';
        htmlRows += '<option value="or">Or</option>';
        htmlRows += '</select>';
        htmlRows += '</td>';
        $('#groupRules').append(htmlRows);
    });
    $(document).on('click', '#remove', function(){
        $(".itemRow:checked").each(function() {
            $(this).closest('tr').remove();
        });
        $('#checkAll').prop('checked', false);
    });
    $('.add-group-company').on('click', function(){
        var gid = $(this).attr('data-id');

        $('#gid').val();
        $('#gid').val(gid);
    });
    $('#allGroups').on('click', '.delete-group', function(){
        var gid = $(this).attr('data-id');

        $('#dgid').val();
        $('#dgid').val(gid);
    });
    $('#allCompanies').on('click', '.delete-company-from-group', function(){
        var cid = $(this).attr('data-id');

        $('#gcid').val();
        $('#gcid').val(cid);
    });

    $('#allWebsites').DataTable({
        pageLength: 15,
        lengthMenu: [15, 30, 45, 60, 75, 90, 105, 120],
        "columnDefs": [{
            "searchable": false,
            "orderable": false,
            "targets": [3]
        }],
        order: [[1, 'desc']],
        responsive: true,
    });
    $('#allWebsites').on('click', '.edit-website', function(){
        var wid = $(this).attr('data-id');

        var csrftoken = $("[name=csrfmiddlewaretoken]").val();

        $.ajax({
            url: "/work/fetch-website-by-id",
            type: "POST",
            dataType: 'json',
            data: {wid:wid, csrfmiddlewaretoken: csrftoken},
            success: function(response){
                $('#wid').val();
                $('#wid').val(wid);
                $('#ddomain').val();
                $('#ddomain').val(response.data.domain);
                $('#dstatus').val();
                $('#dstatus').val(response.data.status);
            },
            error: function(response, errorThrown){
                console.log(errorThrown);
            }, 
        });
    });
    $('#allWebsites').on('click', '.delete-website', function(){
        var wid = $(this).attr('data-id');

        $('#dwid').val();
        $('#dwid').val(wid);
    });

    $('#allVisitors').on('click', '.delete-visitor', function(){
        var visitorid = $(this).attr('data-id');

        $('#dvisitorid').val();
        $('#dvisitorid').val(visitorid);
    });
    $('#allVisits').on('click', '.delete-visit', function(){
        var visitid = $(this).attr('data-id');

        $('#dvisitid').val();
        $('#dvisitid').val(visitid);
    });
    
    
})