<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "masothue1";

$conn = new mysqli($servername, $username, $password, $dbname);
// Kiểm tra kết nối
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$conn->set_charset("utf8mb4");

function getDbConnection() {
    global $conn;
    return $conn;
}
header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = file_get_contents('php://input');
    if ($_GET['type'] === 'location') {
        $decoded_data = json_decode($data);
        foreach ($decoded_data as $item) {
            $name = $item->name;
            $parent_id = $item->parent_id;
            $slug = $item->slug;
            $check_stmt = $conn->prepare("SELECT id FROM tbl1_locations WHERE slug = ?");
            if (!$check_stmt) {
                echo "Prepare failed: (" . $conn->errno . ") " . $conn->error;
                continue;
            }
            $check_stmt->bind_param("s", $slug);
            if ($check_stmt->execute()) {
                $check_result = $check_stmt->get_result();
                if ($check_result->num_rows > 0) {
                    echo "Error: Slug '$slug' already exists. Skipping insertion.<br>";
                    continue;
                }
            } else {
                echo "Error: " . $check_stmt->error . "<br>";
                continue;   
            }
            $check_stmt->close();
            
            if ($parent_id && $parent_id != 0) {
                $sql = "SELECT id FROM tbl1_locations WHERE slug = ?";
                if ($stmt = $conn->prepare($sql)) {
                    $stmt->bind_param("s", $parent_id);
                    $stmt->execute();
                    $stmt->bind_result($id);
                    if ($stmt->fetch()) {
                        $parent_id = $id;
                    } else {
                        echo "Không tìm thấy id cho slug = $parent_id";
                    }
                    $stmt->close();
                } else {
                    echo "Lỗi trong quá trình chuẩn bị câu lệnh SQL: " . $conn->error;
                }
            }
            $insert_stmt = $conn->prepare("INSERT INTO tbl1_locations (name, slug, parent_id) VALUES (?, ?, ?)");
            if (!$insert_stmt) {
                echo "Prepare failed: (" . $conn->errno . ") " . $conn->error . "<br>";
                continue;
            }
            $insert_stmt->bind_param("ssi", $name, $slug, $parent_id);
            if ($insert_stmt->execute()) {
                echo "Record for $name added successfully.<br>";
            } else {
                echo "Error: " . $insert_stmt->error . "<br>";
            }
            $insert_stmt->close();
        }
    } else if ($_GET['type'] == 'companies') {
        $decoded_data = json_decode($data);
        $address = $decoded_data->address ?? '';
        $phone = $decoded_data->phone ?? '';
        $representative = $decoded_data->representative ?? '';
        $business = json_encode($decoded_data->business, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) ?? null;
        $location_slug = $decoded_data->location;
        $tax_code = $decoded_data->tax_code ?? '';
        $address_map = $decoded_data->address_map ?? '';
        $website = $decoded_data->website ?? '';
        $images = json_encode($decoded_data->images, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) ?? null;
        $phone_map = $decoded_data->phone_map ?? '';
        $location_id = '';
        if (!empty($website) && isset($website) || (!empty($images) && is_array($images) && count($images) > 0) || !empty($phone_map) && isset($phone_map) || !empty($address_map) && isset($address_map) || !empty($address_map)) {
            // Check if tax_code already exists
            $stmt_check_tax_code = $conn->prepare("SELECT id FROM tbl1_companies WHERE tax_code = ?");
            if (!$stmt_check_tax_code) {
                echo "Prepare failed: (" . $conn->errno . ") " . $conn->error . "<br>";
                exit;
            }
            $stmt_check_tax_code->bind_param("s", $tax_code);
            if ($stmt_check_tax_code->execute()) {
                $result_tax_code = $stmt_check_tax_code->get_result();
                if ($result_tax_code->num_rows > 0) {
                    echo "Error: A company with tax_code '$tax_code' already exists.<br>";
                    exit;
                }
            } else {
                echo "Error: " . $stmt_check_tax_code->error . "<br>";
                exit;
            }
            $stmt_check_tax_code->close();

            // Check if location_slug exists and get location_id
            $stmt_location = $conn->prepare("SELECT id FROM tbl1_locations WHERE slug = ?");
            if (!$stmt_location) {
                echo "Prepare failed: (" . $conn->errno . ") " . $conn->error . "<br>";
                exit;
            }
            $stmt_location->bind_param("s", $location_slug);
            if ($stmt_location->execute()) {
                $result_location = $stmt_location->get_result();
                if ($result_location->num_rows > 0) {
                    $location_row = $result_location->fetch_assoc();
                    $location_id = $location_row['id'];
                    echo "Location ID for slug '$location_slug' is: " . $location_id . "<br>";
                } else {
                    echo "Error: Location with slug '$location_slug' not found.<br>";
                    exit;
                }
            } else {
                echo "Error: " . $stmt_location->error . "<br>";
                exit;
            }
            $stmt_location->close();

            // Insert new company record
            $stmt_company = $conn->prepare("INSERT INTO tbl1_companies (name, address, phone, busines, location_id, representative, tax_code) VALUES (?, ?, ?, ?, ?, ?, ?)");
            if (!$stmt_company) {
                echo "Prepare failed: (" . $conn->errno . ") " . $conn->error . "<br>";
                exit;
            }
            $stmt_company->bind_param("ssssiss", $decoded_data->name, $decoded_data->address, $decoded_data->phone, $business, $location_id, $representative, $tax_code);
            if ($stmt_company->execute()) {
                $company_id = $stmt_company->insert_id;
                echo "Bản ghi công ty đã được thêm thành công. Company ID: " . $company_id . "<br>";

                if (!empty($website) && isset($website) || (!empty($images) && is_array($images) && count($images) > 0) || !empty($phone_map) && isset($phone_map) || !empty($address_map) && isset($address_map) || !empty($address_map)) {
                    $stmt_company_info = $conn->prepare("INSERT INTO tbl1_company_infos (company_id, phone, website, images, address) VALUES (?, ?, ?, ?, ?)");
                    $stmt_company_info->bind_param("issss", $company_id, $phone_map, $website, $images, $address_map);
                    if ($stmt_company_info->execute()) {
                        echo "Bản ghi thông tin công ty đã được thêm thành công. Company ID: " . $company_id . "<br>";
                    } else {
                        echo "Lỗi: " . $stmt_company_info->error . "<br>";
                    }
                    $stmt_company_info->close();
                }
            } else {
                echo "Error: " . $stmt_company->error . "<br>";
                exit;
            }
            $stmt_company->close();
        } else {
            echo "Error:  No company";
            exit;
        }
    } else if ($_GET['type'] == 'business') {
        $decoded_data = json_decode($data);
        $id = $decoded_data->code ?? '';
        $name = $decoded_data->name ?? '';
        if ($id !== null && $name !== null) {
            $stmt_check_business = $conn->prepare("SELECT id FROM tbl1_business WHERE id = ?");
            if (!$stmt_check_business) {
                echo "Prepare failed: (" . $conn->errno . ") " . $conn->error . "<br>";
                exit;
            }
            $stmt_check_business->bind_param("s", $id);
            if ($stmt_check_business->execute()) {
                $result_business = $stmt_check_business->get_result();
                if ($result_business->num_rows > 0) {
                    echo "Error: A business with ID '$id' already exists.<br>";
                    exit;
                }
            } else {
                echo "Error: " . $stmt_check_business->error . "<br>";
                exit;
            }
            $stmt_check_business->close();

            // Insert new business record
            $stmt = $conn->prepare("INSERT INTO tbl1_business (id, name) VALUES (?, ?)");
            if (!$stmt) {
                echo "Prepare failed: (" . $conn->errno . ") " . $conn->error . "<br>";
                exit;
            }
            $stmt->bind_param("ss", $id, $name);
            if ($stmt->execute()) {
                echo "Dữ liệu của business đã được thêm thành công. ID: " . $id . ", Name: " . $name . "<br>";
            } else {
                echo "Lỗi khi thêm dữ liệu: " . $stmt->error . "<br>";
            }
            $stmt->close();
        } else {
            echo "Thông tin id và name không hợp lệ để thêm dữ liệu.<br>";
        }
    }
} else {
    echo "Phương thức request không hợp lệ.";
}
// Đóng kết nối sau khi xử lý xong
$conn->close();
